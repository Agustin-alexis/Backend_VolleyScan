"""Consulta de sesiones de análisis y marcado como revisadas."""
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .. import alcance
from ..auth import EsEntrenador
from ..comun import leer_booleano, leer_entero
from ..models import SesionAnalisis
from .serializers import SesionDetalleSerializer, SesionListaSerializer


class AnalisisViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [EsEntrenador]

    def get_serializer_class(self):
        return SesionDetalleSerializer if self.action == "retrieve" else SesionListaSerializer

    def get_queryset(self):
        qs = alcance.sesiones_visibles(self.request.user.id).select_related("usuario")
        if self.action == "retrieve":
            qs = qs.prefetch_related("errores", "puntos", "repeticiones")
        p = self.request
        deportista = leer_entero(p, "deportista")
        if deportista is not None:
            qs = qs.filter(usuario_id=deportista)
        tecnica = p.query_params.get("tecnica")
        if tecnica:
            qs = qs.filter(tecnica=tecnica)
        revisado = leer_booleano(p, "revisado")
        if revisado is not None:
            qs = qs.filter(revisado_por_entrenador=revisado)
        return qs.order_by("-creado_en", "-id")

    @action(detail=True, methods=["post"], url_path="revisar")
    def revisar(self, request, pk=None):
        """Marca la sesión como revisada por el entrenador (idempotente)."""
        sesion = self.get_object()
        if not sesion.revisado_por_entrenador:
            SesionAnalisis.objects.filter(pk=sesion.pk).update(
                revisado_por_entrenador=True, fecha_revision=timezone.now()
            )
        sesion = self.get_object()
        return Response(SesionListaSerializer(sesion).data)
