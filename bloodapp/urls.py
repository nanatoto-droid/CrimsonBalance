from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('donations/', views.donation_history, name='donation_history'),
    path('donor/appointments/', views.donor_appointments, name='donor_appointments'),
    path('recipient/history/', views.recipient_history, name='recipient_history'),
    path('request-blood/', views.request_blood, name='request_blood'),
    path('request-appointment/', views.request_appointment, name='request_appointment'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('information/', views.information_center, name='information_center'),
    path('information/new/', views.information_create, name='information_create'),
    path('information/<int:pk>/', views.information_detail, name='information_detail'),
    path('information/<int:pk>/edit/', views.information_edit, name='information_edit'),
    path('information/<int:pk>/delete/', views.information_delete, name='information_delete'),
    path('doctor/donation/<int:donation_id>/process/', views.process_donation, name='process_donation'),
    path('doctor/request/<int:request_id>/fulfill/', views.fulfill_request, name='fulfill_request'),
    path('doctor/appointment/<int:appointment_id>/<str:status>/', views.update_appointment_status, name='update_appointment_status'),

]
