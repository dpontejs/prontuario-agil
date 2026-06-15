"""
Popula o banco com dados de demonstração para a apresentação.

Usuários criados:
  medico   / 12345678  → Dr. Carlos Mendes (Cardiologia)
  paciente / 12345678  → Maria Santos (paciente)
  super    / 12345678  → superusuário (via criar_usuario_padrao)

Execute: python manage.py popular_banco
"""

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from agendamento.models import (
    Agendamento,
    HorarioDisponivel,
    Medico,
    Paciente,
    Prontuario,
)

User = get_user_model()

MEDICOS = [
    {"nome": "Carlos Mendes",   "crm": "RN-12345", "especialidade": "Cardiologia",    "username": "medico"},
    {"nome": "Ana Lima",        "crm": "RN-23456", "especialidade": "Dermatologia",   "username": None},
    {"nome": "Rafael Santos",   "crm": "RN-34567", "especialidade": "Ortopedia",      "username": None},
    {"nome": "Fernanda Costa",  "crm": "RN-45678", "especialidade": "Neurologia",     "username": None},
]

PACIENTE = {
    "nome": "Maria Santos",
    "cpf": "123.456.789-01",
    "email": "maria@email.com",
    "telefone": "(84) 99999-1234",
    "data_nascimento": date(1990, 5, 15),
    "username": "paciente",
}


class Command(BaseCommand):
    help = "Popula o banco com dados de demonstração"

    def add_arguments(self, parser):
        parser.add_argument("--limpar", action="store_true", help="Remove todos os dados antes de popular")

    def handle(self, *args, **options):
        if options["limpar"]:
            Prontuario.objects.all().delete()
            Agendamento.objects.all().delete()
            HorarioDisponivel.objects.all().delete()
            Medico.objects.all().delete()
            Paciente.objects.all().delete()
            User.objects.filter(username__in=["medico", "paciente"]).delete()
            self.stdout.write(self.style.WARNING("Dados removidos."))

        medico_user = self._criar_user("medico", "medico@prontuario.com", "Médico Demo")
        paciente_user = self._criar_user("paciente", "paciente@prontuario.com", "Paciente Demo")

        medicos = self._criar_medicos(medico_user)
        paciente = self._criar_paciente(paciente_user)
        self._criar_horarios_e_demos(medicos, paciente)

        self.stdout.write(self.style.SUCCESS("\n✅ Banco populado com sucesso!\n"))
        self.stdout.write("  Usuário médico:   medico / 12345678")
        self.stdout.write("  Usuário paciente: paciente / 12345678\n")

    def _criar_user(self, username, email, first_name):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": email, "first_name": first_name},
        )
        if created:
            user.set_password("12345678")
            user.save()
            self.stdout.write(f"  Usuário criado: {username}")
        else:
            self.stdout.write(f"  Usuário já existe: {username}")
        return user

    def _criar_medicos(self, medico_user):
        medicos = []
        for m in MEDICOS:
            user = medico_user if m["username"] == "medico" else None
            medico, created = Medico.objects.get_or_create(
                crm=m["crm"],
                defaults={"nome": m["nome"], "especialidade": m["especialidade"], "user": user},
            )
            if not created and medico.user is None and user is not None:
                medico.user = user
                medico.save()
            medicos.append(medico)
            status = "criado" if created else "já existe"
            self.stdout.write(f"  Médico {status}: Dr(a). {medico.nome} ({medico.especialidade})")
        return medicos

    def _criar_paciente(self, paciente_user):
        p = PACIENTE
        paciente, created = Paciente.objects.get_or_create(
            cpf=p["cpf"],
            defaults={
                "nome": p["nome"],
                "email": p["email"],
                "telefone": p["telefone"],
                "data_nascimento": p["data_nascimento"],
                "user": paciente_user,
            },
        )
        if not created and paciente.user is None:
            paciente.user = paciente_user
            paciente.save()
        status = "criado" if created else "já existe"
        self.stdout.write(f"  Paciente {status}: {paciente.nome}")
        return paciente

    def _criar_horarios_e_demos(self, medicos, paciente):
        hoje = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0)

        # ── Horários livres futuros (visíveis na busca) ───────────────────
        horarios_livres = {
            medicos[0]: [hoje + timedelta(days=3, hours=1),   hoje + timedelta(days=5, hours=2),
                         hoje + timedelta(days=7, hours=3),   hoje + timedelta(days=10, hours=1)],
            medicos[1]: [hoje + timedelta(days=2, hours=2),   hoje + timedelta(days=4, hours=3),
                         hoje + timedelta(days=6, hours=1)],
            medicos[2]: [hoje + timedelta(days=1, hours=3),   hoje + timedelta(days=3, hours=2),
                         hoje + timedelta(days=8, hours=2)],
            medicos[3]: [hoje + timedelta(days=4, hours=1),   hoje + timedelta(days=9, hours=3)],
        }
        for medico, datas in horarios_livres.items():
            for dt in datas:
                HorarioDisponivel.objects.get_or_create(medico=medico, data_hora=dt)

        # ── Caso 1: consulta RESERVADA (demonstrar cancelamento) ──────────
        h_reservado, _ = HorarioDisponivel.objects.get_or_create(
            medico=medicos[0],
            data_hora=hoje + timedelta(days=2, hours=1),
            defaults={"is_ocupado": True},
        )
        h_reservado.is_ocupado = True
        h_reservado.save()
        Agendamento.objects.get_or_create(
            horario=h_reservado,
            paciente_id=paciente.id,
            defaults={"status": "RESERVADO"},
        )
        self.stdout.write(f"  Agendamento RESERVADO: {paciente.nome} → Dr. {medicos[0].nome}")

        # ── Caso 2: consulta CONFIRMADA ───────────────────────────────────
        h_confirmado, _ = HorarioDisponivel.objects.get_or_create(
            medico=medicos[1],
            data_hora=hoje - timedelta(days=5, hours=0),
            defaults={"is_ocupado": True},
        )
        h_confirmado.is_ocupado = True
        h_confirmado.save()
        Agendamento.objects.get_or_create(
            horario=h_confirmado,
            paciente_id=paciente.id,
            defaults={"status": "CONFIRMADO"},
        )
        self.stdout.write(f"  Agendamento CONFIRMADO: {paciente.nome} → Dra. {medicos[1].nome}")

        # ── Caso 3: consulta CANCELADA ────────────────────────────────────
        h_cancelado, _ = HorarioDisponivel.objects.get_or_create(
            medico=medicos[2],
            data_hora=hoje - timedelta(days=10, hours=0),
            defaults={"is_ocupado": False},
        )
        Agendamento.objects.get_or_create(
            horario=h_cancelado,
            paciente_id=paciente.id,
            defaults={"status": "CANCELADO"},
        )
        self.stdout.write(f"  Agendamento CANCELADO: {paciente.nome} → Dr. {medicos[2].nome}")

        # ── Caso 4: prontuário FINALIZADO (médico já consultou) ───────────
        h_pront, _ = HorarioDisponivel.objects.get_or_create(
            medico=medicos[0],
            data_hora=hoje - timedelta(days=14, hours=0),
            defaults={"is_ocupado": True},
        )
        h_pront.is_ocupado = True
        h_pront.save()
        Agendamento.objects.get_or_create(
            horario=h_pront,
            paciente_id=paciente.id,
            defaults={"status": "CONFIRMADO"},
        )
        Prontuario.objects.get_or_create(
            paciente=paciente,
            medico=medicos[0],
            defaults={
                "notas_clinicas": (
                    "Paciente relata dor torácica ocasional há 2 semanas, "
                    "sem irradiação. Pressão arterial 130/85 mmHg. "
                    "ECG sem alterações agudas."
                ),
                "diagnostico": "Hipertensão arterial sistêmica leve (CID I10)",
                "prescricao": (
                    "Losartana 50mg — 1 comprimido ao dia (pela manhã).\n"
                    "Reduzir ingestão de sódio. Retorno em 30 dias."
                ),
                "finalizado": True,
            },
        )
        self.stdout.write(f"  Prontuário FINALIZADO: {paciente.nome} por Dr. {medicos[0].nome}")

        # ── Caso 5: prontuário EM ABERTO (demonstrar edição) ─────────────
        h_aberto, _ = HorarioDisponivel.objects.get_or_create(
            medico=medicos[0],
            data_hora=hoje - timedelta(days=2, hours=0),
            defaults={"is_ocupado": True},
        )
        h_aberto.is_ocupado = True
        h_aberto.save()
        Agendamento.objects.get_or_create(
            horario=h_aberto,
            paciente_id=paciente.id,
            defaults={"status": "CONFIRMADO"},
        )
        Prontuario.objects.get_or_create(
            paciente=paciente,
            medico=medicos[0],
            notas_clinicas="Retorno. Paciente relata melhora da pressão arterial.",
            defaults={
                "diagnostico": "Hipertensão controlada — reavaliação",
                "prescricao": "Manter Losartana 50mg. Próximo retorno em 60 dias.",
                "finalizado": False,
            },
        )
        self.stdout.write(f"  Prontuário EM ABERTO: {paciente.nome} por Dr. {medicos[0].nome}")
