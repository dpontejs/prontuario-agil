from rest_framework.permissions import BasePermission


class IsMedico(BasePermission):
    """Permite acesso apenas a usuários vinculados a um Medico."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "medico")
        )


class IsPaciente(BasePermission):
    """Permite acesso apenas a usuários vinculados a um Paciente."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, "paciente")
        )
