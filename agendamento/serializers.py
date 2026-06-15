from rest_framework import serializers

from .models import Agendamento, HorarioDisponivel, Medico, Paciente, Prontuario


class MedicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medico
        fields = ["id", "nome", "crm", "especialidade"]


class HorarioDisponivelSerializer(serializers.ModelSerializer):
    medico = MedicoSerializer(read_only=True)

    class Meta:
        model = HorarioDisponivel
        fields = ["id", "medico", "data_hora", "is_ocupado"]


class AgendamentoSerializer(serializers.ModelSerializer):
    horario = HorarioDisponivelSerializer(read_only=True)
    paciente_nome = serializers.SerializerMethodField()

    class Meta:
        model = Agendamento
        fields = ["id", "horario", "paciente_id", "paciente_nome", "status", "data_criacao"]

    def get_paciente_nome(self, obj):
        try:
            return Paciente.objects.get(pk=obj.paciente_id).nome
        except Paciente.DoesNotExist:
            return None


class ReservarHorarioSerializer(serializers.Serializer):
    horario_id = serializers.IntegerField()
    paciente_id = serializers.IntegerField()


class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = ["id", "nome", "cpf", "email", "telefone", "data_nascimento"]


class ProntuarioSerializer(serializers.ModelSerializer):
    paciente = PacienteSerializer(read_only=True)
    medico = MedicoSerializer(read_only=True)

    class Meta:
        model = Prontuario
        fields = [
            "id",
            "paciente",
            "medico",
            "notas_clinicas",
            "diagnostico",
            "prescricao",
            "data_registro",
            "finalizado",
        ]


class RegistrarProntuarioSerializer(serializers.Serializer):
    paciente_id = serializers.IntegerField()
    notas_clinicas = serializers.CharField()
    diagnostico = serializers.CharField()
    prescricao = serializers.CharField()
    prontuario_id = serializers.IntegerField(required=False, allow_null=True)
    finalizado = serializers.BooleanField(default=False)
