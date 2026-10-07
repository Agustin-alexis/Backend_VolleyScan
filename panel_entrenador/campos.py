"""Campos de serializer compartidos por todas las secciones del panel.

Los campos *Propio solo aceptan ids que pertenezcan al entrenador autenticado
(un id ajeno responde 400), lo que evita accesos a datos de otros entrenadores.
"""
from rest_framework import serializers

from . import alcance
from .models import Horario, Partido, Usuario


class CampoDelEntrenador(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return self.filtrar(self.context["request"].user.id)

    def filtrar(self, entrenador_id):  # pragma: no cover
        raise NotImplementedError


class EquipoPropio(CampoDelEntrenador):
    def filtrar(self, entrenador_id):
        return alcance.equipos_de(entrenador_id)


class DeportistaPropio(CampoDelEntrenador):
    def filtrar(self, entrenador_id):
        return alcance.deportistas_de(entrenador_id)


class HorarioPropio(CampoDelEntrenador):
    def filtrar(self, entrenador_id):
        return Horario.objects.filter(entrenador_id=entrenador_id)


class PartidoPropio(CampoDelEntrenador):
    def filtrar(self, entrenador_id):
        return Partido.objects.filter(entrenador_id=entrenador_id)


class AtletaAgregable(serializers.PrimaryKeyRelatedField):
    """Cualquier atleta activo (para sumarlo a un equipo)."""

    def get_queryset(self):
        return Usuario.objects.filter(rol="atleta", activo=True)


def nombre_completo(usuario):
    return f"{usuario.nombre} {usuario.apellido}".strip() if usuario else None
