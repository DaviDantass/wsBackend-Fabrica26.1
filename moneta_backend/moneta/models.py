from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=14, unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)