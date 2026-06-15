from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import HorarioDisponivel, Medico
from ..services import AgendamentoService


class AgendamentoServiceTest(TestCase):
    def setUp(self) -> None:
        self.medico = Medico.objects.create(
            nome="Dr. House",
            crm="12345",
            especialidade="Infectologia",
        )
        self.horario_livre = HorarioDisponivel.objects.create(
            medico=self.medico,
            data_hora=timezone.now(),
            is_ocupado=False,
        )
        self.horario_ocupado = HorarioDisponivel.objects.create(
            medico=self.medico,
            data_hora=timezone.now(),
            is_ocupado=True,
        )

    def test_deve_reservar_horario_com_sucesso(self) -> None:
        # Given: um horario livre.
        # When: o paciente solicita a reserva.
        agendamento = AgendamentoService.reservar_horario(
            self.horario_livre.id,
            paciente_id=99,
        )

        # Then: o agendamento e reservado e o horario fica ocupado.
        self.assertIsNotNone(agendamento)
        self.assertEqual(agendamento.status, "RESERVADO")

        self.horario_livre.refresh_from_db()
        self.assertTrue(self.horario_livre.is_ocupado)

    def test_deve_lancar_erro_se_horario_ja_estiver_ocupado(self) -> None:
        # Given: um horario ja ocupado.
        # When/Then: uma nova reserva e rejeitada.
        with self.assertRaises(ValidationError):
            AgendamentoService.reservar_horario(
                self.horario_ocupado.id,
                paciente_id=99,
            )
