# api/urls.py
from django.urls import path, include

app_name = 'api'
urlpatterns = [
    path('usuarios/', include('apps.usuarios.api.urls', namespace='api_usuarios')),
    path('reservas/', include('apps.reservas.api.urls', namespace='api_reservas')),
    # adicionar outras APIs do projeto no futuro
]