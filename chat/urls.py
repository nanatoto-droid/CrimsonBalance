from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('room/<int:room_id>/', views.room, name='room'),
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),


]