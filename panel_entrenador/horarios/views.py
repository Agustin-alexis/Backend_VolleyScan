"""CRUD de horarios (filtros: fecha_desde, fecha_hasta, equipo, estado)."""
from rest_framework.exceptions import ValidationError

from ..comun import BaseEntrenador, leer_entero, leer_fecha
from ..models import Horario
from .serializers import HorarioSerializer


ESTADOS_HORARIO = {"programado", "en_curso", "completado", "cancelado"}


class HorarioViewSet(BaseEntrenador):
    queryset = Horario.objects.select_related("equipo", "deportista")
    serializer_class = HorarioSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        p = self.request
        desde, hasta = leer_fecha(p, "fecha_desde"), leer_fecha(p, "fecha_hasta")
        if desde:
            qs = qs.filter(fecha__gte=desde)
        if hasta:
            qs = qs.filter(fecha__lte=hasta)
        equipo = leer_entero(p, "equipo")
        if equipo is not None:
            qs = qs.filter(equipo_id=equipo)
        estado = p.query_params.get("estado")
        if estado:
            if estado not in ESTADOS_HORARIO:
                raise ValidationError({"estado": "Valor no válido."})
            qs = qs.filter(estado=estado)
        return qs.order_by("fecha", "hora_inicio", "id")
