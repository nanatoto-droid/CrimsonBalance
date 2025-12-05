from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donations/', views.donation_history, name='donation_history'),
    path('request-blood/', views.request_blood, name='request_blood'),
    path('request-appointment/', views.request_appointment, name='request_appointment'),
    path('information/', views.information_center, name='information_center'),
]