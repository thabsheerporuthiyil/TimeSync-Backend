# brands/urls.py
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet

router = DefaultRouter()
router.register("", BrandViewSet)

urlpatterns = router.urls
