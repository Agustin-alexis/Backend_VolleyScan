"""Gestión: CRUD de equipos, integrantes y consulta de deportistas."""
from datetime import date

from django.db.models import Count, Q
from rest_framework import viewsets

from .. import alcance
from ..auth import EsEntrenador
from ..comun import BaseEntrenador, Conflicto, leer_booleano, leer_entero
from ..models import Equipo, EquipoDeportista, Usuario
from .serializers import DeportistaSerializer, EquipoSerializer, IntegranteSerializer


class EquipoViewSet(BaseEntrenador):
    queryset = Equipo.objects.all()
    serializer_class = EquipoSerializer

    def get_queryset(self):
        hoy = date.today()
        vigentes = Count(
            "integrantes",
            filter=Q(integrantes__fecha_fin__isnull=True) | Q(integrantes__fecha_fin__gte=hoy),
        )
        return super().get_queryset().annotate(total_deportistas=vigentes).order_by("nombre", "id")

    def perform_destroy(self, instance):
        # Borrar un equipo arrastraría (CASCADE en MySQL) sus partidos y estadísticas.
        if instance.partidos.exists():
            raise Conflicto(
                "El equipo tiene partidos registrados. Desactívalo (activo=false) en lugar de borrarlo."
            )
        instance.delete()


class IntegranteViewSet(viewsets.ModelViewSet):
    permission_classes = [EsEntrenador]
    queryset = EquipoDeportista.objects.select_related("deportista", "equipo")
    serializer_class = IntegranteSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(equipo__entrenador_id=self.request.user.id)
        equipo = leer_entero(self.request, "equipo")
        if equipo is not None:
            qs = qs.filter(equipo_id=equipo)
        if leer_booleano(self.request, "vigentes"):
            qs = qs.filter(Q(fecha_fin__isnull=True) | Q(fecha_fin__gte=date.today()))
        return qs.order_by("equipo_id", "deportista__apellido", "deportista__nombre", "id")


class DeportistaViewSet(viewsets.ReadOnlyModelViewSet):
    """Atletas de mis equipos. Con ?email=<exacto> busca a cualquier atleta
    activo (para agregarlo a un equipo) y devuelve solo datos básicos."""

    permission_classes = [EsEntrenador]
    serializer_class = DeportistaSerializer

    def get_queryset(self):
        email = self.request.query_params.get("email", "").strip()
        if email and self.action == "list":
            return Usuario.objects.filter(rol="atleta", activo=True, email__iexact=email)
        return alcance.deportistas_de(self.request.user.id).order_by("apellido", "nombre", "id")
