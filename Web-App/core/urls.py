from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),  
    path('module/', module, name='module'), 
    path('module/inicio', inicio, name='inicio'), 
    path('login/', CustomLoginView.as_view(), name='login'),
    path('cambiar_contraseña/', login_required(Cambiar_contraseña.as_view()), name='cambiar_contraseña_usuario')
]
