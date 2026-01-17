from django.db import models

# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=100)
    image = models.URLField()
    filter_key = models.CharField(max_length=50, db_index=True)

    def __str__(self):
        return self.title