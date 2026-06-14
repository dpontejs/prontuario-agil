from django.conf import settings
from django.db import models


class Medico(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="medico",
    )
    nome = models.CharField(max_length=100)
    crm = models.CharField(max_length=20, unique=True)
    especialidade = models.CharField(max_length=50)


class Paciente(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paciente",
    )
    nome = models.CharField(max_length=100)
    cpf = models.CharField(max_length=14, unique=True)
    email = models.EmailField()
    telefone = models.CharField(max_length=20, blank=True)
    data_nascimento = models.DateField()


class HorarioDisponivel(models.Model):
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="horarios",
    )
    data_hora = models.DateTimeField()
    is_ocupado = models.BooleanField(default=False)


class Agendamento(models.Model):
    horario = models.ForeignKey(HorarioDisponivel, on_delete=models.CASCADE)
    paciente_id = models.IntegerField()
    status = models.CharField(max_length=20, default="RESERVADO")
    data_criacao = models.DateTimeField(auto_now_add=True)


class Prontuario(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name="prontuarios",
    )
    medico = models.ForeignKey(
        Medico,
        on_delete=models.CASCADE,
        related_name="prontuarios",
    )
    notas_clinicas = models.TextField()
    diagnostico = models.TextField()
    prescricao = models.TextField()
    data_registro = models.DateTimeField(auto_now_add=True)
    finalizado = models.BooleanField(default=False)
