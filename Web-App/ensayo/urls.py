from django.urls import path
from ensayo import views #importará los métodos que generemos en nuestra app
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.conf.urls.static import static



ensayo_urlpatterns = [
    path('ensayo_main/',views.ensayo_main, name='ensayo_main'),  
    #path('ensayo_ver/<str:ensayo_id>',views.ensayo_ver, name='ensayo_ver'),
    path('list_ensayo_active/',views.list_ensayo_active, name='list_ensayo_active'),
    path('list_ensayo_deactivate/',views.list_ensayo_deactivate, name='list_ensayo_deactivate'),  
    #path('ensayo_edit/<ensayo_id>/',views.ensayo_edit, name='ensayo_edit'),
    path('ensayo_deactivate/<str:ensayo_id>',views.ensayo_deactivate,name='ensayo_deactivate'),
    path('ensayo_activate/<ensayo_id>',views.ensayo_activate,name='ensayo_activate'),
    path('ensayo/tiempos/<str:ensayo_id>/', views.list_tiempos_ensayo, name='list_tiempos_ensayo'),


    
    path('ensayo/grafico/<str:ensayo_id>', views.grafico, name='grafico'),

    path('ensayo/tiempos/detalle/<str:tiempo_id>/', views.detalle_tiempo, name='detalle_tiempo'),

    
    ]


if settings.DEBUG:
    ensayo_urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)