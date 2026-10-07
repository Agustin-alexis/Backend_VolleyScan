"""Reglas de alcance: qué datos puede ver y tocar cada entrenador.

Toda consulta del panel parte de aquí o filtra por `entrenador_id`, de modo
que un entrenador nunca accede a datos de otro (protección contra IDOR).
"""
from datetime import date

from django.db.models import Exists, OuterRef, Q

from .models import Configuracion, Equipo, SesionAnalisis, Usuario

# Valores de configuracion.visibilidad_analisis con los que el atleta permite
# que su entrenador vea sus sesiones de análisis. Con "solo" (el valor por
# defecto) o sin fila de configuración, el entrenador NO las ve.
VISIBILIDAD_PERMITIDA = ("entrenador", "equipo", "todos")


def equipos_de(entrenador_id):
    return Equipo.objects.filter(entrenador_id=entrenador_id)


def deportistas_de(entrenador_id):
    """Atletas activos con membresía vigente en algún equipo del entrenador."""
    hoy = date.today()
    return Usuario.objects.filter(
        Q(membresias__fecha_fin__isnull=True) | Q(membresias__fecha_fin__gte=hoy),
        rol="atleta",
        activo=True,
        membresias__equipo__entrenador_id=entrenador_id,
    ).distinct()


def sesiones_visibles(entrenador_id):
    """Sesiones de análisis que este entrenador puede consultar:
    las asignadas a él, o las de atletas de sus equipos que lo permitieron."""
    permitida = Configuracion.objects.filter(
        usuario_id=OuterRef("usuario_id"),
        visibilidad_analisis__in=VISIBILIDAD_PERMITIDA,
    )
    ids_atletas = deportistas_de(entrenador_id).values("id")
    return SesionAnalisis.objects.annotate(atleta_permite=Exists(permitida)).filter(
        Q(entrenador_id=entrenador_id) | Q(usuario_id__in=ids_atletas, atleta_permite=True)
    )
