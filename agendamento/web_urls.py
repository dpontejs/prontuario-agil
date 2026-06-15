from django.urls import path

from .web_views import (
    agendar_view,
    home_view,
    login_view,
    meus_agendamentos_view,
    prontuario_view,
)

urlpatterns = [
    path("", home_view, name="home"),
    path("login/", login_view, name="login"),
    path("agendar/", agendar_view, name="agendar"),
    path("meus-agendamentos/", meus_agendamentos_view, name="meus_agendamentos"),
    path("prontuario/", prontuario_view, name="prontuario"),
]
