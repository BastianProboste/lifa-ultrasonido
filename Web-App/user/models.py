from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField # type: ignore
# Create your models here.

class User(AbstractUser): 
    rut = models.CharField(max_length=11, null=True, blank=False)
    carrera = models.CharField(max_length=30, null=True, blank=True)
    telefono = PhoneNumberField(blank=False, null=True)