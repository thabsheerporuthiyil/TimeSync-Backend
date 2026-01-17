from django.db import models
from brands.models import Brand
from category.models import Category

# Create your models here.

class Product(models.Model):
    brand = models.ForeignKey("brands.Brand", on_delete=models.CASCADE,related_name='products',db_index=True)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE,related_name='products',db_index=True)

    name = models.CharField(max_length=300,db_index=True)
    image = models.URLField(max_length=500)
    price = models.DecimalField(max_digits=10, decimal_places=2, db_index=True)
    stock = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


