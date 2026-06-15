from django.shortcuts import render


def login_view(request):
    return render(request, "agendamento/login.html")


def home_view(request):
    return render(request, "agendamento/home.html")


def agendar_view(request):
    return render(request, "agendamento/agendar.html")


def meus_agendamentos_view(request):
    return render(request, "agendamento/meus_agendamentos.html")


def prontuario_view(request):
    return render(request, "agendamento/prontuario.html")
