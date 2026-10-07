from rest_framework.routers import SimpleRouter

from .views import AnalisisViewSet

router = SimpleRouter(trailing_slash=False)
router.register("analisis", AnalisisViewSet, basename="analisis-panel")

urlpatterns = router.urls
