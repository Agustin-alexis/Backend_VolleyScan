"""Vistas de login: POST /api/auth/login y GET /api/auth/me

Seguridad aplicada:
- Respuesta idéntica y tiempo similar para "usuario inexistente" y "clave
  incorrecta" (hash falso de relleno) → no permite enumerar correos.
- Límite de intentos por IP (scope "login").
"""
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .auth import HASH_RELLENO, crear_token, verificar_password
from .models import Usuario


def resumen_usuario(usuario):
    return {
        "id": usuario.id,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "email": usuario.email,
        "rol": usuario.rol,
        "foto_url": usuario.foto_url,
    }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=150)
    password = serializers.CharField(max_length=128, trim_whitespace=False)


class LoginView(APIView):
    authentication_classes = []  # un token vencido en la cabecera no debe bloquear el login
    permission_classes = [permissions.AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        datos = LoginSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        email = datos.validated_data["email"].strip().lower()
        password = datos.validated_data["password"]

        usuario = Usuario.objects.filter(email=email, activo=True).first()
        almacenado = usuario.password_hash if usuario else HASH_RELLENO
        valida = verificar_password(password, almacenado)

        if usuario is None or not valida:
            return Response(
                {"detail": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED
            )
        return Response({"access": crear_token(usuario), "usuario": resumen_usuario(usuario)})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(resumen_usuario(request.user))