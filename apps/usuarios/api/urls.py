# apps/usuarios/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.usuarios.api.views import (
    UsuarioViewSet,
    UsuarioPublicoViewSet,
    RegistroUsuarioView,
    LoginUsuarioView,
    LogoutUsuarioView,
    MeuPerfilView
)

router = DefaultRouter()
router.register('usuarios', UsuarioViewSet, basename='usuario')
router.register('usuarios-publico', UsuarioPublicoViewSet, basename='usuario-publico')

app_name = 'api_usuarios'

urlpatterns = [
    path('', include(router.urls)),
    path('registro/', RegistroUsuarioView.as_view(), name='registro'),
    path('login/', LoginUsuarioView.as_view(), name='login'),
    path('logout/', LogoutUsuarioView.as_view(), name='logout'),
    path('meu-perfil/', MeuPerfilView.as_view(), name='meu-perfil'),
]