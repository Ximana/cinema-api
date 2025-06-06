from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import TicketReservation

User = get_user_model()


class TicketReservationSerializer(serializers.ModelSerializer):
    """Serializer completo para reservas de ingressos"""
    user_name = serializers.CharField(source='user.get_full_name_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = TicketReservation
        fields = (
            'id', 'total_price', 'user', 'user_name', 'user_email',
            'session', 'seats', 'movie_id', 'status', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'user_name', 'user_email')

    def validate_total_price(self, value):
        """Validar se o preço total é positivo"""
        if value <= 0:
            raise serializers.ValidationError(_('O preço total deve ser maior que zero.'))
        return value
    
    def validate_seats(self, value):
        """Validar se os assentos foram fornecidos"""
        if not value or not value.strip():
            raise serializers.ValidationError(_('Os assentos devem ser especificados.'))
        return value
    
    def validate_movie_id(self, value):
        """Validar se o ID do filme foi fornecido"""
        if not value or not value.strip():
            raise serializers.ValidationError(_('O ID do filme deve ser especificado.'))
        return value


class TicketReservationCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de reservas (sem especificar usuário manualmente)"""
    
    class Meta:
        model = TicketReservation
        fields = (
            'total_price', 'session', 'seats', 'movie_id', 'status'
        )
    
    def validate_total_price(self, value):
        """Validar se o preço total é positivo"""
        if value <= 0:
            raise serializers.ValidationError(_('O preço total deve ser maior que zero.'))
        return value
    
    def validate_seats(self, value):
        """Validar se os assentos foram fornecidos"""
        if not value or not value.strip():
            raise serializers.ValidationError(_('Os assentos devem ser especificados.'))
        return value
    
    def validate_movie_id(self, value):
        """Validar se o ID do filme foi fornecido"""
        if not value or not value.strip():
            raise serializers.ValidationError(_('O ID do filme deve ser especificado.'))
        return value
    
    def create(self, validated_data):
        """Criar reserva associando ao usuário autenticado"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


class TicketReservationPublicSerializer(serializers.ModelSerializer):
    """Serializer para dados públicos da reserva (limitado)"""
    
    class Meta:
        model = TicketReservation
        fields = ('id', 'movie_id', 'session', 'status', 'created_at')


class TicketReservationUpdateStatusSerializer(serializers.ModelSerializer):
    """Serializer específico para atualização do status da reserva"""
    
    class Meta:
        model = TicketReservation
        fields = ('status',)
    
    def validate_status(self, value):
        """Validar transições de status"""
        instance = self.instance
        if instance:
            # Regras de negócio para transição de status
            if instance.status == 'cancelled' and value != 'cancelled':
                raise serializers.ValidationError(_('Não é possível alterar uma reserva cancelada.'))
            
            if instance.status == 'completed' and value != 'completed':
                raise serializers.ValidationError(_('Não é possível alterar uma reserva concluída.'))
        
        return value