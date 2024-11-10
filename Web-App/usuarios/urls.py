from django.urls import path
from .views import *


urlpatterns = [
    path('add_user/', add_user, name='add_user'),
    path('user_list/', user_list, name='user_list'),
    path('edit_user/<int:id>', edit_user, name='edit_user'),
    path('delete_user/<int:id_users>/', delete_user, name='delete_user'),
    path('user_detail/<int:user_id>/', user_detail, name='user_detail'),

]

