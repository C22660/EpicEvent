from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class Users(AbstractUser):
    """Stocke les identifiants de connexion des utilisateurs"""
    first_name = models.CharField(max_length=15, verbose_name="prenom")
    last_name = models.CharField(max_length=15, verbose_name="nom")
    email = models.EmailField(unique=True, max_length=255, blank=False)
    is_sales = models.BooleanField('sales team', default=False)
    is_support = models.BooleanField('support team', default=False)
    is_management = models.BooleanField('management team', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'is_sales', 'is_support', 'is_management']
from django.db import models

# Create your models here.
