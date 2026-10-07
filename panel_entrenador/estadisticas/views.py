"""CRUD de estadísticas y resumen acumulado por deportista."""
from django.db.models import Count, Sum
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ..auth import EsEntrenador
from ..comun import leer_entero, leer_fecha
from ..models import EstadisticaJugador
from .serializers import EstadisticaSerializer


_CAMPOS_SUMA = [
    "saques_exitosos", "saques_fallidos", "ataques_exitosos", "ataques_fallidos",
    "bloqueos", "recepciones_exitosas", "recepciones_falladas",
    "errores_no_forzados", "puntos_totales", "minutos_jugados",
]


def _porcentaje(aciertos, fallos):
    total = aciertos + fallos
    return round(100 * aciertos / total, 1) if total else None


class EstadisticaViewSet(viewsets.ModelViewSet):
    permission_classes = [EsEntrenador]
    queryset = EstadisticaJugador.objects.select_related("deportista", "partido")
    serializer_class = EstadisticaSerializer

    def get_queryset(self):
        qs = super().get_queryset().filter(partido__entrenador_id=self.request.user.id)
        p = self.request
        partido, equipo, deportista = (
            leer_entero(p, "partido"), leer_entero(p, "equipo"), leer_entero(p, "deportista"),
        )
        if partido is not None:
            qs = qs.filter(partido_id=partido)
        if equipo is not None:
            qs = qs.filter(partido__equipo_id=equipo)
        if deportista is not None:
            qs = qs.filter(deportista_id=deportista)
        desde, hasta = leer_fecha(p, "fecha_desde"), leer_fecha(p, "fecha_hasta")
        if desde:
            qs = qs.filter(partido__fecha__gte=desde)
        if hasta:
            qs = qs.filter(partido__fecha__lte=hasta)
        return qs.order_by("partido_id", "deportista__apellido", "id")

    @action(detail=False, methods=["get"], url_path="resumen")
    def resumen(self, request):
        """Totales y porcentajes acumulados por deportista (acepta los mismos filtros)."""
        filas = (
            self.get_queryset()
            .order_by()
            .values("deportista_id", "deportista__nombre", "deportista__apellido")
            .annotate(n_partidos=Count("id"), **{f"t_{c}": Sum(c) for c in _CAMPOS_SUMA})
            .order_by("deportista__apellido", "deportista__nombre")
        )
        resultado = []
        for fila in filas:
            total = {c: fila[f"t_{c}"] or 0 for c in _CAMPOS_SUMA}
            resultado.append(
                {
                    "deportista": fila["deportista_id"],
                    "deportista_nombre": f"{fila['deportista__nombre']} {fila['deportista__apellido']}".strip(),
                    "partidos": fila["n_partidos"],
                    **total,
                    "efectividad_saque": _porcentaje(total["saques_exitosos"], total["saques_fallidos"]),
                    "efectividad_ataque": _porcentaje(total["ataques_exitosos"], total["ataques_fallidos"]),
                    "efectividad_recepcion": _porcentaje(
                        total["recepciones_exitosas"], total["recepciones_falladas"]
                    ),
                }
            )
        return Response(resultado)
