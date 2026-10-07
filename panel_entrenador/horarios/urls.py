from rest_framework.routers import SimpleRouter

from .views import HorarioViewSet

router = SimpleRouter(trailing_slash=False)
router.register("horarios", HorarioViewSet, basename="horario")

urlpatterns = router.urls
