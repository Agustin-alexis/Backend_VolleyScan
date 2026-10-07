from rest_framework.routers import SimpleRouter

from .views import EstadisticaViewSet

router = SimpleRouter(trailing_slash=False)
router.register("estadisticas", EstadisticaViewSet, basename="estadistica")

urlpatterns = router.urls
