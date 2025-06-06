# apps/reservas/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class TicketReservation(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pendente'),
        ('confirmed', 'Confirmada'),
        ('cancelled', 'Cancelada'),
        ('completed', 'Concluída'),
    )
    
    # Campos conforme especificação
    total_price = models.DecimalField(
        'Preço Total',
        max_digits=10,
        decimal_places=2,
        help_text='Preço total da reserva'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuário',
        related_name='reservas'
    )
    session = models.CharField(
        'Sessão',
        max_length=100,
        help_text='Informações da sessão do filme'
    )
    seats = models.TextField(
        'Assentos',
        help_text='Assentos reservados (formato JSON ou string)'
    )
    movie_id = models.CharField(
        'ID do Filme (TMDB)',
        max_length=20,
        help_text='ID do filme no The Movie Database'
    )
    status = models.CharField(
        'Status',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Campos de controle
    created_at = models.DateTimeField('Criado em', auto_now_add=True)
    updated_at = models.DateTimeField('Atualizado em', auto_now=True)
    
    class Meta:
        db_table = 'ticketReservation'  # nome da tabela
        verbose_name = 'Reserva de Ingresso'
        verbose_name_plural = 'Reservas de Ingressos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Reserva #{self.id} - {self.user.get_full_name_display()}'
    
    def get_absolute_url(self):
        return reverse('administracao:reserva_detalhe', kwargs={'pk': self.pk})
    
    def is_active(self):
        """Verifica se a reserva está ativa (confirmada ou pendente)"""
        return self.status in ['pending', 'confirmed']
    
    def can_be_cancelled(self):
        """Verifica se a reserva pode ser cancelada"""
        return self.status in ['pending', 'confirmed']
