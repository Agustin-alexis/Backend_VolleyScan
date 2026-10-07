"""Horarios y eventos del entrenador."""
from rest_framework import serializers

from ..campos import DeportistaPropio, EquipoPropio, nombre_completo
from ..models import Equipo, Horario, Usuario


class HorarioSerializer(serializers.ModelSerializer):
    equipo = EquipoPropio(queryset=Equipo.objects.none(), required=False, allow_null=True)
    deportista = DeportistaPropio(
        queryset=Usuario.objects.none(), required=False, allow_null=True
    )
    equipo_nombre = serializers.SerializerMethodField()
    deportista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Horario
        fields = [
            "id", "equipo", "equipo_nombre", "deportista", "deportista_nombre",
            "titulo", "tipo_evento", "fecha", "hora_inicio", "hora_fin",
            "ubicacion", "estado", "notas", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_equipo_nombre(self, obj):
        return obj.equipo.nombre if obj.equipo else None

    def get_deportista_nombre(self, obj):
        return nombre_completo(obj.deportista)

    def validate(self, attrs):
        base = self.instance
        inicio = attrs.get("hora_inicio", getattr(base, "hora_inicio", None))
        fin = attrs.get("hora_fin", getattr(base, "hora_fin", None))
        if inicio and fin and fin <= inicio:
            raise serializers.ValidationError(
                {"hora_fin": "Debe ser posterior a la hora de inicio."}
            )
        return attrs
