"""Resumen general del panel."""
from datetime import date, timedelta

from rest_framework.response import Response
from rest_framework.views import APIView

from .. import alcance
from ..auth import EsEntrenador
from ..models import Equipo, Horario, Partido


class DashboardView(APIView):
    permission_classes = [EsEntrenador]

    def get(self, request):
        eid = request.user.id
        hoy = date.today()
        proximos = (
            Horario.objects.filter(
                entrenador_id=eid, estado="programado",
                fecha__gte=hoy, fecha__lte=hoy + timedelta(days=7),
            )
            .order_by("fecha", "hora_inicio")
            .values("id", "titulo", "tipo_evento", "fecha", "hora_inicio", "hora_fin", "ubicacion")[:10]
        )
        ultimos = (
            Partido.objects.filter(entrenador_id=eid)
            .order_by("-fecha", "-id")
            .values("id", "rival", "fecha", "sets_ganados", "sets_perdidos")[:5]
        )
        return Response(
            {
                "equipos_activos": Equipo.objects.filter(entrenador_id=eid, activo=True).count(),
                "deportistas_activos": alcance.deportistas_de(eid).count(),
                "analisis_pendientes": alcance.sesiones_visibles(eid)
                .filter(revisado_por_entrenador=False)
                .count(),
                "eventos_proximos": list(proximos),
                "ultimos_partidos": list(ultimos),
            }
        )
