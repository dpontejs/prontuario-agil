from datetime import date

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from ..models import Medico


class PacienteModelTest(TestCase):
    def test_paciente_pode_existir_sem_usuario(self) -> None:
        from ..models import Paciente

        # Given: dados validos sem um usuario associado.
        # When: o paciente e criado.
        paciente = Paciente.objects.create(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@example.com",
            telefone="84999990000",
            data_nascimento=date(1990, 5, 10),
        )

        # Then: o vinculo opcional permanece vazio.
        self.assertIsNone(paciente.user)

    def test_paciente_pode_ser_vinculado_a_usuario(self) -> None:
        from ..models import Paciente

        # Given: um usuario autenticavel.
        user = get_user_model().objects.create_user(username="ana")

        # When: um paciente e criado com esse usuario.
        paciente = Paciente.objects.create(
            user=user,
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@example.com",
            telefone="84999990000",
            data_nascimento=date(1990, 5, 10),
        )

        # Then: o relacionamento e persistido.
        paciente.refresh_from_db()
        self.assertEqual(paciente.user, user)

    def test_cpf_de_paciente_deve_ser_unico(self) -> None:
        from ..models import Paciente

        # Given: um paciente cadastrado com determinado CPF.
        Paciente.objects.create(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@example.com",
            telefone="84999990000",
            data_nascimento=date(1990, 5, 10),
        )

        # When/Then: outro paciente com o mesmo CPF e rejeitado pelo banco.
        with self.assertRaises(IntegrityError), transaction.atomic():
            Paciente.objects.create(
                nome="Bruna Lima",
                cpf="12345678901",
                email="bruna@example.com",
                telefone="84999991111",
                data_nascimento=date(1988, 8, 20),
            )


class MedicoModelTest(TestCase):
    def test_medico_pode_existir_sem_usuario(self) -> None:
        # Given: dados validos sem um usuario associado.
        # When: o medico e criado.
        medico = Medico.objects.create(
            nome="Dr. Gregory House",
            crm="CRM-001",
            especialidade="Infectologia",
        )

        # Then: o vinculo opcional permanece vazio.
        self.assertIsNone(medico.user)

    def test_medico_pode_ser_vinculado_a_usuario(self) -> None:
        # Given: um usuario autenticavel.
        user = get_user_model().objects.create_user(username="house")

        # When: um medico e criado com esse usuario.
        medico = Medico.objects.create(
            user=user,
            nome="Dr. Gregory House",
            crm="CRM-001",
            especialidade="Infectologia",
        )

        # Then: o relacionamento e persistido.
        medico.refresh_from_db()
        self.assertEqual(medico.user, user)


class ProntuarioModelTest(TestCase):
    def test_prontuario_persiste_relacionamentos_e_dados_clinicos(self) -> None:
        from ..models import Prontuario
        from ..models import Paciente

        # Given: um paciente e um medico cadastrados.
        paciente = Paciente.objects.create(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@example.com",
            telefone="84999990000",
            data_nascimento=date(1990, 5, 10),
        )
        medico = Medico.objects.create(
            nome="Dra. Maria Lima",
            crm="CRM-002",
            especialidade="Cardiologia",
        )

        # When: um prontuario finalizado e registrado.
        prontuario = Prontuario.objects.create(
            paciente=paciente,
            medico=medico,
            notas_clinicas="Dor toracica ha tres dias.",
            diagnostico="Angina estavel",
            prescricao="AAS 100 mg",
            finalizado=True,
        )

        # Then: relacionamentos, campos e estado sao persistidos.
        prontuario.refresh_from_db()
        self.assertEqual(prontuario.paciente, paciente)
        self.assertEqual(prontuario.medico, medico)
        self.assertEqual(prontuario.notas_clinicas, "Dor toracica ha tres dias.")
        self.assertEqual(prontuario.diagnostico, "Angina estavel")
        self.assertEqual(prontuario.prescricao, "AAS 100 mg")
        self.assertTrue(prontuario.finalizado)

    def test_prontuario_registra_timestamp_e_inicia_aberto(self) -> None:
        from ..models import Paciente
        from ..models import Prontuario

        # Given: um paciente e um medico cadastrados.
        paciente = Paciente.objects.create(
            nome="Ana Souza",
            cpf="12345678901",
            email="ana@example.com",
            telefone="84999990000",
            data_nascimento=date(1990, 5, 10),
        )
        medico = Medico.objects.create(
            nome="Dra. Maria Lima",
            crm="CRM-002",
            especialidade="Cardiologia",
        )
        instante_inicial = timezone.now()

        # When: um prontuario e criado sem informar estado ou data.
        prontuario = Prontuario.objects.create(
            paciente=paciente,
            medico=medico,
            notas_clinicas="Consulta inicial.",
            diagnostico="Em investigacao",
            prescricao="Exames complementares",
        )

        # Then: a data e automatica e o registro inicia nao finalizado.
        self.assertGreaterEqual(prontuario.data_registro, instante_inicial)
        self.assertLessEqual(prontuario.data_registro, timezone.now())
        self.assertFalse(prontuario.finalizado)
