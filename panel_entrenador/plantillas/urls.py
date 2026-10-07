from rest_framework.routers import SimpleRouter

from .views import PlantillaViewSet

router = SimpleRouter(trailing_slash=False)
router.register("plantillas", PlantillaViewSet, basename="plantilla")

urlpatterns = router.urls
