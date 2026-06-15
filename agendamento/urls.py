from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendamentoViewSet,
    HorarioDisponivelViewSet,
    MedicoViewSet,
    PacienteViewSet,
    ProntuarioViewSet,
    me,
)

router = DefaultRouter()
router.register("medicos", MedicoViewSet, basename="medico")
router.register("horarios", HorarioDisponivelViewSet, basename="horario")
router.register("agendamentos", AgendamentoViewSet, basename="agendamento")
router.register("prontuarios", ProntuarioViewSet, basename="prontuario")
router.register("pacientes", PacienteViewSet, basename="paciente")

urlpatterns = [
    path("me/", me, name="me"),
    path("", include(router.urls)),
]
