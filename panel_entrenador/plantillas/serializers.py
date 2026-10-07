"""Rutinas: plantillas con ejercicios y asignación a atletas."""
import re

from django.db import transaction
from rest_framework import serializers

from ..campos import DeportistaPropio
from ..models import PlantillaEjercicio, RutinaPlantilla, Usuario


MAX_EJERCICIOS_PLANTILLA = 100


class PlantillaEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlantillaEjercicio
        fields = [
            "id", "nombre_ejercicio", "series", "repeticiones",
            "descanso_segundos", "orden", "notas",
        ]
        read_only_fields = ["id"]


class PlantillaSerializer(serializers.ModelSerializer):
    ejercicios = PlantillaEjercicioSerializer(many=True, required=False)

    class Meta:
        model = RutinaPlantilla
        fields = [
            "id", "nombre", "descripcion", "categoria", "nivel",
            "duracion_minutos", "ejercicios", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_ejercicios(self, valor):
        if len(valor) > MAX_EJERCICIOS_PLANTILLA:
            raise serializers.ValidationError(
                f"Máximo {MAX_EJERCICIOS_PLANTILLA} ejercicios por plantilla."
            )
        return valor

    @staticmethod
    def _guardar_ejercicios(plantilla, ejercicios):
        PlantillaEjercicio.objects.bulk_create(
            [PlantillaEjercicio(plantilla=plantilla, **e) for e in ejercicios]
        )

    @transaction.atomic
    def create(self, validated_data):
        ejercicios = validated_data.pop("ejercicios", [])
        plantilla = RutinaPlantilla.objects.create(**validated_data)
        self._guardar_ejercicios(plantilla, ejercicios)
        return plantilla

    @transaction.atomic
    def update(self, instance, validated_data):
        # Si llega "ejercicios", la lista REEMPLAZA a la anterior.
        ejercicios = validated_data.pop("ejercicios", None)
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save()
        if ejercicios is not None:
            PlantillaEjercicio.objects.filter(plantilla=instance).delete()
            self._guardar_ejercicios(instance, ejercicios)
        return instance


class AsignarRutinaSerializer(serializers.Serializer):
    deportista = DeportistaPropio(queryset=Usuario.objects.none())


_RE_ENTERO = re.compile(r"\s*(\d+)")


def a_tinyint(valor, defecto):
    """Convierte "8-10", 12 o None en un entero válido para TINYINT UNSIGNED."""
    if valor is None:
        return defecto
    coincidencia = _RE_ENTERO.match(str(valor))
    if not coincidencia:
        return defecto
    return min(int(coincidencia.group(1)), 255)
