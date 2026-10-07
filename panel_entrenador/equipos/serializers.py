"""Gestión: equipos, integrantes y deportistas."""
from datetime import date

from rest_framework import serializers

from ..campos import AtletaAgregable, EquipoPropio, nombre_completo
from ..models import Equipo, EquipoDeportista, Usuario


class EquipoSerializer(serializers.ModelSerializer):
    total_deportistas = serializers.IntegerField(read_only=True)

    class Meta:
        model = Equipo
        fields = [
            "id", "nombre", "categoria", "temporada", "activo",
            "total_deportistas", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class DeportistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nombre", "apellido", "email", "nivel", "posicion", "foto_url"]
        read_only_fields = fields


class IntegranteSerializer(serializers.ModelSerializer):
    equipo = EquipoPropio(queryset=Equipo.objects.none())
    deportista = AtletaAgregable(queryset=Usuario.objects.none())
    deportista_nombre = serializers.SerializerMethodField()

    class Meta:
        model = EquipoDeportista
        fields = [
            "id", "equipo", "deportista", "deportista_nombre", "fecha_inicio",
            "fecha_fin", "posicion", "numero_camiseta",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {"fecha_inicio": {"required": False}}

    def get_deportista_nombre(self, obj):
        return nombre_completo(obj.deportista)

    def validate(self, attrs):
        if self.instance is not None:
            attrs.pop("equipo", None)  # inmutables tras crear
            attrs.pop("deportista", None)
            inicio = attrs.get("fecha_inicio", self.instance.fecha_inicio)
            fin = attrs.get("fecha_fin", self.instance.fecha_fin)
        else:
            attrs.setdefault("fecha_inicio", date.today())
            inicio = attrs["fecha_inicio"]
            fin = attrs.get("fecha_fin")
            repetido = EquipoDeportista.objects.filter(
                equipo=attrs["equipo"], deportista=attrs["deportista"]
            )
            if repetido.filter(fecha_fin__isnull=True).exists() or repetido.filter(
                fecha_inicio=inicio
            ).exists():
                raise serializers.ValidationError(
                    {"deportista": "Ya existe una membresía vigente o igual en este equipo."}
                )
        if fin and fin < inicio:
            raise serializers.ValidationError(
                {"fecha_fin": "No puede ser anterior a la fecha de inicio."}
            )
        return attrs
