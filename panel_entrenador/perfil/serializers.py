"""Perfil del entrenador."""
from datetime import date

from rest_framework import serializers

from ..models import Usuario


class PerfilSerializer(serializers.ModelSerializer):
    foto_url = serializers.URLField(
        max_length=500, required=False, allow_null=True, allow_blank=True
    )

    class Meta:
        model = Usuario
        fields = [
            "id", "nombre", "apellido", "email", "rol", "nivel", "posicion",
            "peso", "estatura", "fecha_nac", "foto_url",
        ]
        read_only_fields = ["id", "email", "rol"]
        extra_kwargs = {
            "peso": {"min_value": 20, "max_value": 300},
            "estatura": {"min_value": 0.5, "max_value": 2.5},
        }

    def validate_fecha_nac(self, valor):
        if valor and valor > date.today():
            raise serializers.ValidationError("No puede estar en el futuro.")
        return valor

    def validate_foto_url(self, valor):
        if valor and not valor.lower().startswith(("http://", "https://")):
            raise serializers.ValidationError("Solo se permiten enlaces http o https.")
        return valor

    def update(self, instance, validated_data):
        # update_fields: nunca reescribe password_hash ni columnas no editadas.
        for campo, valor in validated_data.items():
            setattr(instance, campo, valor)
        instance.save(update_fields=list(validated_data))
        return instance
