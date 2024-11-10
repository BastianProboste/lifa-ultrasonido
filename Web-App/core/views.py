from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages

# Create your views here.

# Página home
def home(request):
    return render(request, 'core/home.html')


# Página de administración
@login_required
def module(request):
    return render(request, 'core/module.html')

# Redirección a pagina principal
class CustomLoginView(LoginView):
    def form_invalid(self, form):
        if form.errors.get('__all__'):  # Error genérico de usuario/contraseña
            messages.error(self.request, "Usuario o contraseña incorrectos.")
        elif form.errors.get('username'):  # Usuario no existe
            messages.error(self.request, "El usuario no existe.")
        return redirect('/')
