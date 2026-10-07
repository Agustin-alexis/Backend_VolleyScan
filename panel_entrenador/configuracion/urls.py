from django.urls import path

from .views import ConfiguracionView

urlpatterns = [path("configuracion", ConfiguracionView.as_view(), name="panel-configuracion")]
