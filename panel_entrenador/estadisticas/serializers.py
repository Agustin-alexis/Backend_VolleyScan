"""Estadísticas por jugador y partido."""
from rest_framework import serializers

from ..campos import DeportistaPropio, PartidoPropio, nombre_completo
from ..models import EquipoDeportista, EstadisticaJugador, Partido, Usuario


class EstadisticaSerializer(serializers.ModelSerializer):
    partido = PartidoPropio(queryset=Partido.objects.none())
    deportista = DeportistaPropio(queryset=Usuario.objects.none())
    deportista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = EstadisticaJugador
        fields = [
            "id", "partido", "deportista", "deportista_nombre",
            "saques_exitosos", "saques_fallidos", "ataques_exitosos",
            "ataques_fallidos", "bloqueos", "recepciones_exitosas",
            "recepciones_falladas", "errores_no_forzados", "puntos_totales",
            "minutos_jugados",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {"minutos_jugados": {"max_value": 300}}

    def get_deportista_nombre(self, obj):
        return nombre_completo(obj.deportista)

    def validate(self, attrs):
        if self.instance is not None:
            attrs.pop("partido", None)
            attrs.pop("deportista", None)
            return attrs
        partido, deportista = attrs["partido"], attrs["deportista"]
        if not EquipoDeportista.objects.filter(
            equipo_id=partido.equipo_id, deportista=deportista
        ).exists():
            raise serializers.ValidationError(
                {"deportista": "No pertenece al equipo de este partido."}
            )
        if EstadisticaJugador.objects.filter(partido=partido, deportista=deportista).exists():
            raise serializers.ValidationError(
                {"deportista": "Ya hay estadísticas de este deportista en el partido."}
            )
        return attrs
