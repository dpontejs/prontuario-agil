from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Cria o usuário padrão do sistema (super@mail.com / 12345678)"

    def handle(self, *args, **options):
        User = get_user_model()
        if User.objects.filter(email="super@mail.com").exists():
            self.stdout.write(self.style.WARNING("Usuário super@mail.com já existe."))
            return
        User.objects.create_superuser(
            username="super",
            email="super@mail.com",
            password="12345678",
        )
        self.stdout.write(self.style.SUCCESS("Usuário padrão criado: super@mail.com / 12345678"))
