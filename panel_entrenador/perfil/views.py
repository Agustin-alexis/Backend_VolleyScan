"""GET y PATCH del perfil propio."""
from rest_framework import generics

from ..auth import EsEntrenador
from ..models import Usuario
from .serializers import PerfilSerializer


class PerfilView(generics.RetrieveUpdateAPIView):
    """GET y PATCH del perfil propio. El correo y el rol no se pueden cambiar aquí."""

    permission_classes = [EsEntrenador]
    serializer_class = PerfilSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return Usuario.objects.get(pk=self.request.user.pk)
