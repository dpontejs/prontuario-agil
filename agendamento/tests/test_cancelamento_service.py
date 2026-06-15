from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from ..models import Agendamento, HorarioDisponivel, Medico
from ..services import AgendamentoService


class CancelamentoServiceTest(TestCase):
    def setUp(self) -> None:
        medico = Medico.objects.create(
            nome="Dra. Maria Lima",
            crm="CRM-002",
            especialidade="Cardiologia",
        )
        self.horario = HorarioDisponivel.objects.create(
            medico=medico,
            data_hora=timezone.now(),
            is_ocupado=True,
        )

    def test_cancelar_agendamento_muda_status_e_libera_horario(self) -> None:
        # Given: um agendamento reservado em um horario ocupado.
        agendamento = Agendamento.objects.create(
            horario=self.horario,
            paciente_id=42,
            status="RESERVADO",
        )

        # When: o cancelamento e solicitado.
        cancelado = AgendamentoService.cancelar_agendamento(agendamento.id)

        # Then: o status muda e o horario volta a ficar disponivel.
        cancelado.refresh_from_db()
        self.horario.refresh_from_db()
        self.assertEqual(cancelado.status, "CANCELADO")
        self.assertFalse(self.horario.is_ocupado)

    def test_cancelar_agendamento_ja_cancelado_preserva_estado(self) -> None:
        # Given: um agendamento ja cancelado e seu horario livre.
        self.horario.is_ocupado = False
        self.horario.save(update_fields=["is_ocupado"])
        agendamento = Agendamento.objects.create(
            horario=self.horario,
            paciente_id=42,
            status="CANCELADO",
        )

        # When/Then: novo cancelamento e rejeitado.
        with self.assertRaises(ValidationError):
            AgendamentoService.cancelar_agendamento(agendamento.id)

        # Then: nenhum estado persistido e alterado.
        agendamento.refresh_from_db()
        self.horario.refresh_from_db()
        self.assertEqual(agendamento.status, "CANCELADO")
        self.assertFalse(self.horario.is_ocupado)
