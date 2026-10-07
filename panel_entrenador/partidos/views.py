"""CRUD de partidos (filtros: equipo, fecha_desde, fecha_hasta)."""
from ..comun import BaseEntrenador, leer_entero, leer_fecha
from ..models import Partido
from .serializers import PartidoSerializer


class PartidoViewSet(BaseEntrenador):
    queryset = Partido.objects.select_related("equipo")
    serializer_class = PartidoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        equipo = leer_entero(self.request, "equipo")
        if equipo is not None:
            qs = qs.filter(equipo_id=equipo)
        desde, hasta = leer_fecha(self.request, "fecha_desde"), leer_fecha(self.request, "fecha_hasta")
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        return qs.order_by("-fecha", "-id")
