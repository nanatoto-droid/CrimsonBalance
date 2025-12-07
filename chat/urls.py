from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('room/<int:room_id>/', views.room, name='room'),
    path('start/<int:user_id>/', views.start_chat, name='start_chat'),
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),
    path('start-with-message/', views.start_chat_with_message, name='start_chat_with_message'),
]