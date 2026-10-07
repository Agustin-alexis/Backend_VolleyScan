"""CRUD de plantillas y asignación (copia) a un atleta."""
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..comun import BaseEntrenador
from ..models import EjercicioRutina, Rutina, RutinaPlantilla
from .serializers import AsignarRutinaSerializer, PlantillaSerializer, a_tinyint


class PlantillaViewSet(BaseEntrenador):
    queryset = RutinaPlantilla.objects.prefetch_related("ejercicios")
    serializer_class = PlantillaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        categoria = self.request.query_params.get("categoria")
        if categoria:
            qs = qs.filter(categoria=categoria)
        return qs.order_by("nombre", "id")

    @action(detail=True, methods=["post"], url_path="asignar")
    def asignar(self, request, pk=None):
        """Copia la plantilla como rutina personal de un atleta de mis equipos."""
        plantilla = self.get_object()
        datos = AsignarRutinaSerializer(
            data=request.data, context=self.get_serializer_context()
        )
        datos.is_valid(raise_exception=True)
        atleta = datos.validated_data["deportista"]

        with transaction.atomic():
            rutina = Rutina.objects.create(
                usuario=atleta,
                entrenador_id=request.user.id,
                plantilla_id=plantilla.id,
                nombre=plantilla.nombre,
                descripcion=plantilla.descripcion,
                nivel=plantilla.nivel,
                objetivo=plantilla.categoria,
                generada_por_ia=False,
                activa=True,
            )
            EjercicioRutina.objects.bulk_create(
                [
                    EjercicioRutina(
                        rutina=rutina,
                        nombre=e.nombre_ejercicio,
                        series=a_tinyint(e.series, 3),
                        repeticiones=a_tinyint(e.repeticiones, 10),
                        orden=a_tinyint(e.orden, 1),
                    )
                    for e in plantilla.ejercicios.all()
                ]
            )
        return Response({"rutina_id": rutina.id}, status=status.HTTP_201_CREATED)
