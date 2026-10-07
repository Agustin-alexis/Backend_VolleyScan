from rest_framework.routers import SimpleRouter

from .views import PartidoViewSet

router = SimpleRouter(trailing_slash=False)
router.register("partidos", PartidoViewSet, basename="partido")

urlpatterns = router.urls
