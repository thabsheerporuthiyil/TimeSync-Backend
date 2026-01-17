# brands/views.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import Brand
from .serializers import BrandSerializer


class BrandViewSet(ReadOnlyModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
