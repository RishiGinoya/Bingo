from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('health/', views.health_check, name='health_check'),  # Health check for keep-alive
    path('join/', views.join_room, name='join_room'),     # Action to join
    path('create/', views.create_room, name='create_room'), # Action to create
    path('room/<str:room_code>/', views.room, name='room'),
]