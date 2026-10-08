from django.urls import path
from . import views

urlpatterns = [
    # Rutas públicas independientes
    path('', views.inicio, name='inicio'),
    path('servicios/', views.servicios_view, name='servicios'),
    path('reserva/', views.reserva_view, name='reserva'),
    path('reserva/confirmada/', views.reserva_confirmada_view, name='reserva_confirmada'),
    path('contacto/', views.contacto_view, name='contacto'),
    
    # API para disponibilidad en tiempo real
    path('api/disponibilidad/', views.api_disponibilidad, name='api_disponibilidad'),

    # Rutas de administración protegida
    path('admin/', views.admin_dashboard_view, name='admin_root'),
    path('admin/login/', views.admin_login_view, name='admin_login'),
    path('admin/logout/', views.admin_logout_view, name='admin_logout'),
    path('admin/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/reservas/', views.admin_reservas_view, name='admin_reservas'),
    path('admin/servicios/', views.admin_servicios_view, name='admin_servicios'),
    path('admin/horarios/', views.admin_horarios_view, name='admin_horarios'),
]
