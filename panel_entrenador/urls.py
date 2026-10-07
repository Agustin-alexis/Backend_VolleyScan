"""Rutas del panel. En volleyscan/urls.py:  path("api/", include("panel_entrenador.urls"))

Sin barra final: POST /api/auth/login, GET /api/panel/equipos, etc.
"""
from django.urls import include, path

from .login import LoginView, MeView

urlpatterns = [
    path("auth/login", LoginView.as_view(), name="login"),
    path("auth/me", MeView.as_view(), name="me"),
    path("panel/", include("panel_entrenador.equipos.urls")),
    path("panel/", include("panel_entrenador.horarios.urls")),
    path("panel/", include("panel_entrenador.plantillas.urls")),
    path("panel/", include("panel_entrenador.partidos.urls")),
    path("panel/", include("panel_entrenador.estadisticas.urls")),
    path("panel/", include("panel_entrenador.analisis.urls")),
    path("panel/", include("panel_entrenador.dashboard.urls")),
    path("panel/", include("panel_entrenador.perfil.urls")),
    path("panel/", include("panel_entrenador.configuracion.urls")),
]