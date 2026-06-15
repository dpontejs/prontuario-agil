from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase

from ..models import Medico
from ..services import AgendamentoService


class ProntuarioServiceTest(TestCase):
    def test_registrar_prontuario_cria_registro_clinico(self) -> None:
        registrar_prontuario = AgendamentoService.registrar_prontuario
        from ..models import Paciente

        # Given: um paciente, um medico e os dados do atendimento.
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

        # When: o service registra o prontuario.
        prontuario = registrar_prontuario(
            paciente_id=paciente.id,
            medico_id=medico.id,
            notas_clinicas="Dor toracica ha tres dias.",
            diagnostico="Angina estavel",
            prescricao="AAS 100 mg",
        )

        # Then: os dados clinicos e relacionamentos sao persistidos.
        prontuario.refresh_from_db()
        self.assertEqual(prontuario.paciente, paciente)
        self.assertEqual(prontuario.medico, medico)
        self.assertEqual(prontuario.notas_clinicas, "Dor toracica ha tres dias.")
        self.assertEqual(prontuario.diagnostico, "Angina estavel")
        self.assertEqual(prontuario.prescricao, "AAS 100 mg")
        self.assertFalse(prontuario.finalizado)

    def test_editar_prontuario_finalizado_preserva_dados(self) -> None:
        registrar_prontuario = AgendamentoService.registrar_prontuario
        from ..models import Paciente, Prontuario

        # Given: um prontuario finalizado com dados clinicos persistidos.
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
        prontuario = Prontuario.objects.create(
            paciente=paciente,
            medico=medico,
            notas_clinicas="Dados originais.",
            diagnostico="Diagnostico original",
            prescricao="Prescricao original",
            finalizado=True,
        )

        # When/Then: atualizar ou finalizar novamente e rejeitado.
        with self.assertRaises(ValidationError):
            registrar_prontuario(
                paciente_id=paciente.id,
                medico_id=medico.id,
                notas_clinicas="Dados alterados.",
                diagnostico="Diagnostico alterado",
                prescricao="Prescricao alterada",
                prontuario_id=prontuario.id,
                finalizado=True,
            )

        # Then: os valores originais permanecem intactos.
        prontuario.refresh_from_db()
        self.assertEqual(prontuario.notas_clinicas, "Dados originais.")
        self.assertEqual(prontuario.diagnostico, "Diagnostico original")
        self.assertEqual(prontuario.prescricao, "Prescricao original")
        self.assertTrue(prontuario.finalizado)
