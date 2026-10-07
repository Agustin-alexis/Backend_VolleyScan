"""Utilidades compartidas por las vistas de todas las secciones."""
from datetime import date

from rest_framework import status, viewsets
from rest_framework.exceptions import APIException, ValidationError

from .auth import EsEntrenador


class Conflicto(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "La operación entra en conflicto con datos existentes."
    default_code = "conflicto"


def leer_fecha(request, nombre):
    valor = request.query_params.get(nombre)
    if not valor:
        return None
    try:
        return date.fromisoformat(valor)
    except ValueError:
        raise ValidationError({nombre: "Formato esperado: AAAA-MM-DD."})


def leer_entero(request, nombre):
    valor = request.query_params.get(nombre)
    if not valor:
        return None
    try:
        return int(valor)
    except ValueError:
        raise ValidationError({nombre: "Debe ser un número entero."})


def leer_booleano(request, nombre):
    valor = request.query_params.get(nombre)
    if valor is None or valor == "":
        return None
    if valor.lower() in ("true", "1"):
        return True
    if valor.lower() in ("false", "0"):
        return False
    raise ValidationError({nombre: "Use true o false."})


class BaseEntrenador(viewsets.ModelViewSet):
    """CRUD de tablas con columna entrenador_id: solo ve/edita lo propio."""

    permission_classes = [EsEntrenador]

    def get_queryset(self):
        return super().get_queryset().filter(entrenador_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(entrenador_id=self.request.user.id)
