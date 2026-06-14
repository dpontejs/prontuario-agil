from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendamentoViewSet,
    HorarioDisponivelViewSet,
    MedicoViewSet,
    ProntuarioViewSet,
)

router = DefaultRouter()
router.register("medicos", MedicoViewSet, basename="medico")
router.register("horarios", HorarioDisponivelViewSet, basename="horario")
router.register("agendamentos", AgendamentoViewSet, basename="agendamento")
router.register("prontuarios", ProntuarioViewSet, basename="prontuario")

urlpatterns = [
    path("", include(router.urls)),
]
