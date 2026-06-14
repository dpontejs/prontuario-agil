from django.core.exceptions import ValidationError
from django.db import transaction

from .models import (
    Agendamento,
    HorarioDisponivel,
    Medico,
    Paciente,
    Prontuario,
)


class AgendamentoService:
    @staticmethod
    @transaction.atomic
    def reservar_horario(horario_id: int, paciente_id: int) -> Agendamento:
        try:
            horario = HorarioDisponivel.objects.select_for_update().get(
                pk=horario_id,
            )
        except HorarioDisponivel.DoesNotExist:
            raise ValidationError("Horário não encontrado.") from None

        if horario.is_ocupado:
            raise ValidationError(
                "Este horário já está reservado ou confirmado.",
            )

        horario.is_ocupado = True
        horario.save(update_fields=["is_ocupado"])

        return Agendamento.objects.create(
            horario=horario,
            paciente_id=paciente_id,
            status="RESERVADO",
        )

    @staticmethod
    @transaction.atomic
    def cancelar_agendamento(agendamento_id: int) -> Agendamento:
        try:
            agendamento = Agendamento.objects.select_for_update().get(
                pk=agendamento_id,
            )
        except Agendamento.DoesNotExist:
            raise ValidationError("Agendamento não encontrado.") from None

        if agendamento.status == "CANCELADO":
            raise ValidationError("Agendamento já está cancelado.")

        try:
            horario = HorarioDisponivel.objects.select_for_update().get(
                pk=agendamento.horario_id,
            )
        except HorarioDisponivel.DoesNotExist:
            raise ValidationError("Horário não encontrado.") from None

        agendamento.status = "CANCELADO"
        agendamento.save(update_fields=["status"])
        horario.is_ocupado = False
        horario.save(update_fields=["is_ocupado"])
        return agendamento

    @staticmethod
    @transaction.atomic
    def registrar_prontuario(
        paciente_id: int,
        medico_id: int,
        notas_clinicas: str,
        diagnostico: str,
        prescricao: str,
        prontuario_id: int | None = None,
        finalizado: bool = False,
    ) -> Prontuario:
        if prontuario_id is None:
            try:
                paciente = Paciente.objects.get(pk=paciente_id)
            except Paciente.DoesNotExist:
                raise ValidationError("Paciente não encontrado.") from None

            try:
                medico = Medico.objects.get(pk=medico_id)
            except Medico.DoesNotExist:
                raise ValidationError("Médico não encontrado.") from None

            return Prontuario.objects.create(
                paciente=paciente,
                medico=medico,
                notas_clinicas=notas_clinicas,
                diagnostico=diagnostico,
                prescricao=prescricao,
                finalizado=finalizado,
            )

        try:
            prontuario = Prontuario.objects.select_for_update().get(
                pk=prontuario_id,
            )
        except Prontuario.DoesNotExist:
            raise ValidationError("Prontuário não encontrado.") from None

        if prontuario.finalizado:
            raise ValidationError("Prontuário finalizado não pode ser alterado.")

        try:
            paciente = Paciente.objects.get(pk=paciente_id)
        except Paciente.DoesNotExist:
            raise ValidationError("Paciente não encontrado.") from None

        try:
            medico = Medico.objects.get(pk=medico_id)
        except Medico.DoesNotExist:
            raise ValidationError("Médico não encontrado.") from None

        prontuario.paciente = paciente
        prontuario.medico = medico
        prontuario.notas_clinicas = notas_clinicas
        prontuario.diagnostico = diagnostico
        prontuario.prescricao = prescricao
        prontuario.finalizado = finalizado
        prontuario.save(
            update_fields=[
                "paciente",
                "medico",
                "notas_clinicas",
                "diagnostico",
                "prescricao",
                "finalizado",
            ],
        )
        return prontuario
