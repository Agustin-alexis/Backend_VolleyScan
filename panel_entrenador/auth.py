"""Autenticación del panel: verificación de contraseña, token JWT y permiso de entrenador.

IMPORTANTE: este módulo NO debe importar rest_framework.views (ni nada que lo
importe). Django REST Framework carga JWTAuthentication desde los ajustes al
importar sus vistas; si este archivo importara las vistas habría un import
circular. Las vistas de login viven en login.py.

Seguridad aplicada:
- La contraseña se compara con bcrypt (o con los hashers de Django si el hash
tiene otro formato). Nunca se devuelve ni se registra el hash.
- El rol se lee SIEMPRE de la base de datos, no del token: si se desactiva o
se cambia el rol de un usuario, el efecto es inmediato.
- Token firmado HS256 con SECRET_KEY, con vencimiento (PANEL_JWT_HORAS, 8 por defecto).
"""
import datetime as dt

import bcrypt
import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password as django_check_password
from rest_framework import authentication, exceptions, permissions

from .models import Usuario

JWT_ALGORITMO = "HS256"
JWT_HORAS = int(getattr(settings, "PANEL_JWT_HORAS", 8))

# Hash de relleno para igualar el tiempo de respuesta cuando el correo no existe.
HASH_RELLENO = bcrypt.hashpw(b"relleno-no-valido", bcrypt.gensalt()).decode()


def verificar_password(plano, almacenado):
    try:
        if almacenado.startswith(("$2a$", "$2b$", "$2y$")):
            # bcrypt solo considera los primeros 72 bytes.
            return bcrypt.checkpw(plano.encode("utf-8")[:72], almacenado.encode("utf-8"))
        return django_check_password(plano, almacenado)
    except (ValueError, TypeError):
        return False


def crear_token(usuario):
    ahora = dt.datetime.now(dt.timezone.utc)
    payload = {
        "sub": str(usuario.id),
        "iat": ahora,
        "exp": ahora + dt.timedelta(hours=JWT_HORAS),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITMO)


class JWTAuthentication(authentication.BaseAuthentication):
    """Authorization: Bearer <token>"""

    def authenticate(self, request):
        partes = authentication.get_authorization_header(request).split()
        if not partes or partes[0].lower() != b"bearer":
            return None
        if len(partes) != 2:
            raise exceptions.AuthenticationFailed("Token inválido.")
        try:
            payload = jwt.decode(
                partes[1].decode("utf-8"),
                settings.SECRET_KEY,
                algorithms=[JWT_ALGORITMO],
                options={"require": ["exp", "sub"]},
            )
            usuario = Usuario.objects.get(pk=int(payload["sub"]), activo=True)
        except (jwt.PyJWTError, UnicodeError, ValueError, Usuario.DoesNotExist):
            raise exceptions.AuthenticationFailed("Token inválido o vencido.")
        return (usuario, None)

    def authenticate_header(self, request):
        return "Bearer"


class EsEntrenador(permissions.BasePermission):
    message = "Solo disponible para entrenadores."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario
            and getattr(usuario, "is_authenticated", False)
            and getattr(usuario, "rol", None) == "entrenador"
        )