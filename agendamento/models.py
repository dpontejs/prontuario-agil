from django.db import models

class Medico(models.Model):
    nome=models.CharField(max_length=100)
    crm= models.CharField(max_length=20, unique=True)
    especialidade= models.CharField(max_length=50)

class HorarioDisponivel(models.Model):
    medico= models.ForeignKey(Medico , on_delete=models.CASCADE, related_name="horarios")
    data_hora= models.DateTimeField()
    is_ocupado= models.BooleanField(default=False)

class Agendamento(models.Model):
    horario= models.ForeignKey( HorarioDisponivel, on_delete=models.CASCADE)
    paciente_id= models.IntegerField()
    status= models.CharField(max_length=20,default="RESERVADO")
    data_criacao= models.DateTimeField(auto_now_add= True)

    
