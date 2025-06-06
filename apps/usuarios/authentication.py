# apps/usuarios/authentication.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailAuthenticationBackend(BaseBackend):
    """
    Autenticador personalizado que permite login apenas com email
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Procurar usuário pelo email
            user = User.objects.get(email=username)
            # Verificar a senha
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
