"""GET y PATCH de la configuración propia."""
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth import EsEntrenador
from ..models import Configuracion
from .serializers import ConfiguracionSerializer


class ConfiguracionView(APIView):
    permission_classes = [EsEntrenador]

    def get(self, request):
        config = Configuracion.objects.filter(usuario_id=request.user.id).first()
        # Sin fila guardada se devuelven los valores por defecto (sin crear nada).
        return Response(ConfiguracionSerializer(config or Configuracion()).data)

    def patch(self, request):
        config, _ = Configuracion.objects.get_or_create(usuario_id=request.user.id)
        datos = ConfiguracionSerializer(config, data=request.data, partial=True)
        datos.is_valid(raise_exception=True)
        datos.save()
        return Response(datos.data)
