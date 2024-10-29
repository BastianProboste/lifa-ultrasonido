from django.urls import path
from .views import *


urlpatterns = [
    path('', home, name='home'),  
    path('module/', module, name='module'), 
    path('login/', CustomLoginView.as_view(), name='login'),
]
