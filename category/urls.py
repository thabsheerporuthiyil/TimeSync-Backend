from category.views import CategoryViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("categories", CategoryViewSet)
urlpatterns = router.urls