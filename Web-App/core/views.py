from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

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
        return redirect('/')
