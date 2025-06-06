#apps/core/urls.py
from django.urls import path
from .views import usuarios_views
from .views import reservas_views
from . import views
from django.shortcuts import render

app_name = 'administracao'

urlpatterns = [
    
    path('', views.home_view, name='home'),
   
    # Usuarios
    path('login/', usuarios_views.login_view, name='login'),
    path('logout/', usuarios_views.logout_view, name='logout'),
    path('usuarios/lista/', usuarios_views.UserListView.as_view(), name='usuarios_lista'),
    path('usuarios/detalhe/<int:pk>/', usuarios_views.UserDetailView.as_view(), name='usuario_detalhe'),
    path('usuarios/remover/<int:pk>/', usuarios_views.UserDeleteView.as_view(), name='usuario_remover'),
    path('usuarios/atualizar/', usuarios_views.UserUpdateView.as_view(), name='usuario_atualizar'),    
    path('usuario/senha/alterar/', usuarios_views.ChangePasswordView.as_view(), name='usuario_alterar_senha'), 

    # URLs para Reservas
    path('reservas/', reservas_views.TicketReservationListView.as_view(), name='reservas_lista'),
    path('reservas/<int:pk>/', reservas_views.TicketReservationDetailView.as_view(), name='reserva_detalhe'),
    path('reservas/<int:pk>/status/', reservas_views.TicketReservationUpdateStatusView.as_view(), name='reserva_update_status'),
    #path('reservas/<int:pk>/print/', reservas_views.TicketReservationPrintView.as_view(), name='reserva_print'),
    
    
    # Filmes
   
    # Unidades/Cinemas
   
    # URLs para assentos
  
    
]