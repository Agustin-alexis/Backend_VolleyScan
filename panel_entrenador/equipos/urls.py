from rest_framework.routers import SimpleRouter

from .views import DeportistaViewSet, EquipoViewSet, IntegranteViewSet

router = SimpleRouter(trailing_slash=False)
router.register("equipos", EquipoViewSet, basename="equipo")
router.register("integrantes", IntegranteViewSet, basename="integrante")
router.register("deportistas", DeportistaViewSet, basename="deportista")

urlpatterns = router.urls
