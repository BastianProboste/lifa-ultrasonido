from django.urls import path
from ensayo import views 
from django.conf import settings
from django.conf.urls.static import static



ensayo_urlpatterns = [
    path('ensayo_main/',views.ensayo_main, name='ensayo_main'),  
    path('listado_ensayo_active/',views.listado_ensayo_active, name='listado_ensayo_active'),
    path('listado_ensayo_deactivate/',views.listado_ensayo_deactivate, name='listado_ensayo_deactivate'),  
    path('ensayo_deactivate/<str:ensayo_id>',views.ensayo_deactivate,name='ensayo_deactivate'),
    path('ensayo_activate/<ensayo_id>',views.ensayo_activate,name='ensayo_activate'),
    path('ensayo/tiempos/<str:ensayo_id>/', views.listado_tiempos_ensayo, name='listado_tiempos_ensayo'),   
    path('ensayo/grafico/<str:ensayo_id>', views.grafico, name='grafico'),
    path('ensayo/tiempos/detalle/<str:tiempo_id>/', views.detalle_tiempo, name='detalle_tiempo'),
    path('agregar-rut/<str:ensayo_id>/', views.agregar_rut_ensayo, name='agregar_rut_ensayo'),

    
    ]


if settings.DEBUG:
    ensayo_urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)