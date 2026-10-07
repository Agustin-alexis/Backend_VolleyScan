"""Partidos del entrenador."""
from rest_framework import serializers

from ..campos import EquipoPropio, HorarioPropio
from ..models import Equipo, Horario, Partido


class PartidoSerializer(serializers.ModelSerializer):
    equipo = EquipoPropio(queryset=Equipo.objects.none())
    horario = HorarioPropio(queryset=Horario.objects.none(), required=False, allow_null=True)
    equipo_nombre = serializers.SerializerMethodField()
    resultado = serializers.SerializerMethodField()

    class Meta:
        model = Partido
        fields = [
            "id", "equipo", "equipo_nombre", "horario", "rival", "fecha",
            "sets_ganados", "sets_perdidos", "resultado", "ubicacion",
            "notas", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
        extra_kwargs = {
            "sets_ganados": {"max_value": 5},
            "sets_perdidos": {"max_value": 5},
        }

    def get_equipo_nombre(self, obj):
        return obj.equipo.nombre if obj.equipo else None

    def get_resultado(self, obj):
        if obj.sets_ganados > obj.sets_perdidos:
            return "victoria"
        if obj.sets_ganados < obj.sets_perdidos:
            return "derrota"
        return "empate"

    def validate(self, attrs):
        if self.instance is not None:
            attrs.pop("equipo", None)  # un partido no cambia de equipo
        return attrs
