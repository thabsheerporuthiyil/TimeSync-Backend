from django.db import models

# Create your models here.
class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    logo = models.URLField()

    def __str__(self):
        return self.name
