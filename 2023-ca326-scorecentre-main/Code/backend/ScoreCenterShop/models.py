from dataclasses import is_dataclass
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class APIUser(AbstractUser):
    pass

class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0) #9999.99
    image = models.FileField(upload_to='products', null=True)
