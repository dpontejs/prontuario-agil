from django.core.exceptions import ValidationError
from .models import HorarioDisponivel, Agendamento

class AgendamentoService:
    @staticmethod
    def reservar_horario(horario_id: int, paciente_id: int) -> Agendamento:
        try:
            horario = HorarioDisponivel.objects.get(pk=horario_id)
        except HorarioDisponivel.DoesNotExist:
            raise ValidationError("Horário não encontrado.")

        # Regra de negócio: impede agendamento duplicado
        if horario.is_ocupado:
            raise ValidationError("Este horário já está reservado ou confirmado.")

        # Atualiza o estado do horário e salva a reserva
        horario.is_ocupado = True
        horario.save()

        return Agendamento.objects.create(
            horario=horario,
            paciente_id=paciente_id,
            status='RESERVADO'
        )