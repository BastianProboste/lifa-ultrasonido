from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.models import BaseUserManager
global contraseña_aleatoria
from user.models import User

class CustomAddUserForm(UserCreationForm):
    class Meta:
        User = get_user_model()
        model = User
        
        fields = ['username', 'rut', 'first_name', 'last_name', 'carrera', 'phone', 'email', 'is_staff']

    password1 = forms.CharField(required=False)
    password2 = forms.CharField(required=False)


    def setPassword(self, contraseña):
        user = super().save(commit=False)

        user.set_password(contraseña)
        user.save()

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

        return user
    