from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from user.models import User
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash

# Create your views here.

# Página home
def home(request):
    return render(request, 'core/home.html')

def inicio(request):
    return render(request, 'core/inicio.html')

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
    
class Cambiar_contraseña(PasswordChangeView):
    template_name = 'core/cambiar_contraseña.html'
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_changed'] = self.request.session.get('password_changed', False)
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Cambio de contraseña exitoso')
        update_session_auth_hash(self.request, form.user)
        self.request.session['password_changed'] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        for field in form:
            for error in field.errors:
                messages.error(self.request, error)
            return super().form_invalid(form)
        