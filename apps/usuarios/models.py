# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Administrador'),
        ('regular', 'Regular'),
    )
    
    # Campos obrigatórios conforme especificação
    full_name = models.CharField(
        'Nome Completo',
        max_length=255,
        help_text='Nome completo do usuário'
    )
    email = models.EmailField(
        'Email',
        max_length=100,
        unique=True
    )
    identification_number = models.CharField(
        'Número de Identificação',
        max_length=50,
        unique=True,
        help_text='Número de identificação do usuário (BI, NIF)'
    )
    date_of_birth = models.DateField(
        'Data de Nascimento',
        null=True,
        blank=True
    )
    user_type = models.CharField(
        'Tipo de Usuário',
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='regular'
    )
    
    # Campos de controle (herdados do AbstractUser: password, is_active, date_joined, last_login)
    
    def get_full_name_display(self):
        """Retorna o nome completo do usuário."""
        return self.full_name or self.get_full_name() or self.username
    
    def is_admin_user(self):
        """Verifica se o usuário é um administrador."""
        return self.user_type == 'admin'
    
    class Meta:
        db_table = 'user'  # nome da tabela
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
        ordering = ['full_name']
    
    def __str__(self):
        return self.get_full_name_display()
    
    def get_absolute_url(self):
        return reverse('administracao:usuario_detalhe', kwargs={'pk': self.pk})