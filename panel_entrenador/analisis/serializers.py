"""Análisis de IA de los deportistas (solo lectura)."""
from rest_framework import serializers

from ..campos import nombre_completo
from ..models import ErrorDetectado, PuntoClave, RepeticionAnalisis, SesionAnalisis


class ErrorDetectadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorDetectado
        fields = ["tipo_error", "severidad", "ocurrencias", "descripcion"]
        read_only_fields = fields


class PuntoClaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoClave
        fields = ["nombre", "aprobado", "angulo_grados"]
        read_only_fields = fields


class RepeticionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepeticionAnalisis
        fields = [
            "numero", "registrada_en", "valida", "puntuacion", "brazo",
            "motivo_descarte", "duracion_vuelo_ms", "altura_salto",
            "version_estandar", "medidas",
        ]
        read_only_fields = fields


class SesionListaSerializer(serializers.ModelSerializer):
    deportista_id = serializers.IntegerField(source="usuario_id", read_only=True)
    deportista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = SesionAnalisis
        fields = [
            "id", "deportista_id", "deportista_nombre", "tecnica", "puntuacion",
            "total_repeticiones", "repeticiones_validas", "mejor_puntuacion",
            "duracion_seg", "creado_en", "revisado_por_entrenador", "fecha_revision",
        ]
        read_only_fields = fields

    def get_deportista_nombre(self, obj):
        return nombre_completo(obj.usuario)


class SesionDetalleSerializer(SesionListaSerializer):
    errores = ErrorDetectadoSerializer(many=True, read_only=True)
    puntos_clave = PuntoClaveSerializer(source="puntos", many=True, read_only=True)
    repeticiones = RepeticionSerializer(many=True, read_only=True)

    class Meta(SesionListaSerializer.Meta):
        fields = SesionListaSerializer.Meta.fields + [
            "video_url", "miniatura_url", "modelo_ia", "version_estandar",
            "errores", "puntos_clave", "repeticiones",
        ]
        read_only_fields = fields
