from django.core.exceptions import ValidationError
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Agendamento, HorarioDisponivel, Medico, Paciente, Prontuario
from .permissions import IsMedico
from .serializers import (
    AgendamentoSerializer,
    HorarioDisponivelSerializer,
    MedicoSerializer,
    PacienteSerializer,
    ProntuarioSerializer,
    RegistrarProntuarioSerializer,
    ReservarHorarioSerializer,
)
from .services import AgendamentoService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    user = request.user
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_medico": hasattr(user, "medico"),
        "is_paciente": hasattr(user, "paciente"),
        "paciente_id": user.paciente.id if hasattr(user, "paciente") else None,
        "medico_id": user.medico.id if hasattr(user, "medico") else None,
        "medico_nome": user.medico.nome if hasattr(user, "medico") else None,
        "is_superuser": user.is_superuser,
    }
    return Response(data)


class MedicoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = MedicoSerializer

    def get_queryset(self):
        qs = Medico.objects.all()
        especialidade = self.request.query_params.get("especialidade")
        if especialidade:
            qs = qs.filter(especialidade__icontains=especialidade)
        return qs


class HorarioDisponivelViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = HorarioDisponivelSerializer

    def get_queryset(self):
        qs = HorarioDisponivel.objects.select_related("medico").all()
        medico_id = self.request.query_params.get("medico")
        disponivel = self.request.query_params.get("disponivel")
        if medico_id:
            qs = qs.filter(medico_id=medico_id)
        if disponivel == "true":
            qs = qs.filter(is_ocupado=False)
        return qs


class AgendamentoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = AgendamentoSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Agendamento.objects.select_related("horario__medico")
        if hasattr(user, "medico"):
            return qs.filter(horario__medico=user.medico)
        if hasattr(user, "paciente"):
            return qs.filter(paciente_id=user.paciente.id)
        return qs.all()

    def create(self, request):
        serializer = ReservarHorarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            agendamento = AgendamentoService.reservar_horario(
                horario_id=serializer.validated_data["horario_id"],
                paciente_id=serializer.validated_data["paciente_id"],
            )
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            AgendamentoSerializer(agendamento).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        try:
            agendamento = AgendamentoService.cancelar_agendamento(int(pk))
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AgendamentoSerializer(agendamento).data)

    @action(detail=True, methods=["post"])
    def confirmar(self, request, pk=None):
        try:
            agendamento = AgendamentoService.confirmar_agendamento(int(pk))
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(AgendamentoSerializer(agendamento).data)


class PacienteViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = PacienteSerializer
    queryset = Paciente.objects.all().order_by("nome")


class ProntuarioViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsMedico]
    serializer_class = ProntuarioSerializer

    def get_queryset(self):
        return Prontuario.objects.select_related("paciente", "medico").all()

    def create(self, request):
        serializer = RegistrarProntuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            medico = request.user.medico
            prontuario = AgendamentoService.registrar_prontuario(
                paciente_id=data["paciente_id"],
                medico_id=medico.id,
                notas_clinicas=data["notas_clinicas"],
                diagnostico=data["diagnostico"],
                prescricao=data["prescricao"],
                prontuario_id=data.get("prontuario_id"),
                finalizado=data.get("finalizado", False),
            )
        except ValidationError as exc:
            return Response({"detail": exc.message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            ProntuarioSerializer(prontuario).data,
            status=status.HTTP_201_CREATED,
        )
