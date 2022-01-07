from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, AbstractBaseUser
from django.db import models

# Create your models here.


# class Users(AbstractUser):
#     """Stocke les identifiants de connexion des utilisateurs"""
#     first_name = models.CharField(max_length=15, verbose_name="prenom")
#     last_name = models.CharField(max_length=15, verbose_name="nom")
#     email = models.EmailField(unique=True, max_length=255)
#     is_sales = models.BooleanField('sales team', default=False)
#     is_support = models.BooleanField('support team', default=False)
#     is_management = models.BooleanField('management team', default=False)
#     # username = None
#
#     # choix de l'email et nom du prénom, car plusieurs prénoms identiques possibles
#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['first_name', 'last_name']rManager

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        if not email:
            raise ValueError("Email obligatoire")

        # vérification de la conformité du mail
        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        user = self.create_user(email=email, password=password)
        user.is_admin = True
        user.save()
        return user


class Users(AbstractBaseUser):
    """Stocke les identifiants de connexion des utilisateurs"""
    first_name = models.CharField(max_length=15, verbose_name="prenom")
    last_name = models.CharField(max_length=15, verbose_name="nom")
    email = models.EmailField(unique=True, max_length=255)
    is_sales = models.BooleanField('sales team', default=False)
    is_support = models.BooleanField('support team', default=False)
    is_management = models.BooleanField('management team', default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    # choix de l'email et nom du prénom, car plusieurs prénoms identiques possibles
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    objects = MyUserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
