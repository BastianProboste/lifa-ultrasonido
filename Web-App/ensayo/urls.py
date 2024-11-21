from django.urls import path
from ensayo import views 
from django.conf import settings
from django.conf.urls.static import static



ensayo_urlpatterns = [
    path('ensayo_main/',views.ensayo_main, name='ensayo_main'),  
    path('list_ensayo_active/',views.listado_ensayo_active, name='list_ensayo_active'),
    path('list_ensayo_deactivate/',views.listado_ensayo_deactivate, name='list_ensayo_deactivate'),  
    path('ensayo_deactivate/<str:ensayo_id>',views.ensayo_deactivate,name='ensayo_deactivate'),
    path('ensayo_activate/<ensayo_id>',views.ensayo_activate,name='ensayo_activate'),
    path('ensayo/tiempos/<str:ensayo_id>/', views.listado_tiempos_ensayo, name='list_tiempos_ensayo'),
    path('ensayo/<str:ensayo_id>/agregar_rut/', views.agregar_rut_ensayo, name='agregar_rut_ensayo'),    
    path('ensayo/grafico/<str:ensayo_id>', views.grafico, name='grafico'),
    path('ensayo/tiempos/detalle/<str:tiempo_id>/', views.detalle_tiempo, name='detalle_tiempo'),

    
    ]


if settings.DEBUG:
    ensayo_urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)