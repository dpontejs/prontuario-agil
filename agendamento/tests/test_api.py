from datetime import date

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from ..models import Agendamento, HorarioDisponivel, Medico, Paciente, Prontuario

User = get_user_model()


def _token(client, user):
    res = client.post("/api/token/", {"username": user.username, "password": "senha123"})
    return res.data["access"]


class AutenticacaoAPITest(APITestCase):
    def test_endpoint_protegido_sem_token_retorna_401(self):
        res = self.client.get("/api/medicos/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_endpoint_protegido_com_token_retorna_200(self):
        user = User.objects.create_user(username="paciente1", password="senha123")
        token = _token(self.client, user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        res = self.client.get("/api/medicos/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AgendamentoAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="senha123")
        token = _token(self.client, self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
        self.medico = Medico.objects.create(nome="Dr. House", crm="CRM-001", especialidade="Infectologia")
        self.horario = HorarioDisponivel.objects.create(
            medico=self.medico, data_hora=timezone.now(), is_ocupado=False
        )

    def test_reservar_horario_livre_retorna_201(self):
        res = self.client.post("/api/agendamentos/", {"horario_id": self.horario.id, "paciente_id": 1})
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["status"], "RESERVADO")

    def test_reservar_horario_ocupado_retorna_400(self):
        self.horario.is_ocupado = True
        self.horario.save()
        res = self.client.post("/api/agendamentos/", {"horario_id": self.horario.id, "paciente_id": 1})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancelar_agendamento_libera_horario(self):
        agendamento = Agendamento.objects.create(
            horario=self.horario, paciente_id=1, status="RESERVADO"
        )
        self.horario.is_ocupado = True
        self.horario.save()
        res = self.client.post(f"/api/agendamentos/{agendamento.id}/cancelar/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["status"], "CANCELADO")
        self.horario.refresh_from_db()
        self.assertFalse(self.horario.is_ocupado)


class ProntuarioAutorizacaoTest(APITestCase):
    def setUp(self):
        self.paciente_user = User.objects.create_user(username="paciente2", password="senha123")
        self.medico_user = User.objects.create_user(username="medico2", password="senha123")
        self.medico = Medico.objects.create(
            user=self.medico_user, nome="Dra. Lima", crm="CRM-002", especialidade="Cardiologia"
        )
        self.paciente = Paciente.objects.create(
            nome="Ana", cpf="00011122233", email="ana@test.com",
            telefone="84999990000", data_nascimento=date(1990, 1, 1)
        )

    def _login(self, user):
        token = _token(self.client, user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    def test_paciente_nao_pode_criar_prontuario_retorna_403(self):
        self._login(self.paciente_user)
        res = self.client.post("/api/prontuarios/", {
            "paciente_id": self.paciente.id,
            "notas_clinicas": "teste",
            "diagnostico": "teste",
            "prescricao": "teste",
        })
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_medico_pode_criar_prontuario_retorna_201(self):
        self._login(self.medico_user)
        res = self.client.post("/api/prontuarios/", {
            "paciente_id": self.paciente.id,
            "notas_clinicas": "Dor torácica.",
            "diagnostico": "Angina",
            "prescricao": "AAS 100mg",
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data["diagnostico"], "Angina")

    def test_editar_prontuario_finalizado_retorna_400(self):
        self._login(self.medico_user)
        prontuario = Prontuario.objects.create(
            paciente=self.paciente, medico=self.medico,
            notas_clinicas="original", diagnostico="original", prescricao="original",
            finalizado=True,
        )
        res = self.client.post("/api/prontuarios/", {
            "paciente_id": self.paciente.id,
            "notas_clinicas": "alterado",
            "diagnostico": "alterado",
            "prescricao": "alterado",
            "prontuario_id": prontuario.id,
        })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
