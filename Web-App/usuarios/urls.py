from django.urls import path
from .views import *

# URLS para modulo de usuarios
urlpatterns = [
    path('agregar_usuario/', agregar_usuario, name='agregar_usuario'),
    path('lista_de_usuarios/', lista_de_usuarios, name='lista_de_usuarios'),
    path('editar_usuario/<int:id>', editar_usuario, name='editar_usuario'),
    path('eliminar_usuario/<int:id_users>/', eliminar_usuario, name='eliminar_usuario'),
    path('detalles_usuario/<int:user_id>/', detalles_usuario, name='detalles_usuario'),

]

