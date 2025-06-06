# apps/reservas/api/views.py
from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.contrib.auth import get_user_model

from ..models import TicketReservation
from ..serializers import (
    TicketReservationSerializer,
    TicketReservationCreateSerializer,
    TicketReservationPublicSerializer,
    TicketReservationUpdateStatusSerializer
)

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão personalizada que permite apenas ao próprio usuário 
    ou administradores acessarem as reservas
    """
    def has_object_permission(self, request, view, obj):
        # Administradores podem acessar qualquer reserva
        if request.user and request.user.is_admin_user():
            return True
        
        # Usuários podem acessar apenas suas próprias reservas
        return obj.user == request.user


class TicketReservationViewSet(viewsets.ModelViewSet):
    """ViewSet para operações CRUD de reservas de ingressos"""
    queryset = TicketReservation.objects.all()
    
    def get_serializer_class(self):
        """Retornar serializer adequado para cada ação"""
        if self.action == 'create':
            return TicketReservationCreateSerializer
        elif self.action == 'update_status':
            return TicketReservationUpdateStatusSerializer
        return TicketReservationSerializer
    
    def get_permissions(self):
        """Permissões personalizadas para diferentes ações"""
        if self.action == 'list':
            # Usuários autenticados podem listar (filtrado por usuário)
            return [permissions.IsAuthenticated()]
        elif self.action == 'create':
            # Usuários autenticados podem criar reservas
            return [permissions.IsAuthenticated()]
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # Usuário pode ver/editar suas próprias reservas ou admin pode ver/editar qualquer uma
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        """Filtra o queryset baseado no tipo de usuário"""
        user = self.request.user
        
        if user.is_admin_user():
            # Administradores podem ver todas as reservas
            queryset = TicketReservation.objects.all()
        else:
            # Usuários comuns só podem ver suas próprias reservas
            queryset = TicketReservation.objects.filter(user=user)
        
        # Filtros opcionais
        status_filter = self.request.query_params.get('status', None)
        movie_id_filter = self.request.query_params.get('movie_id', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if movie_id_filter:
            queryset = queryset.filter(movie_id=movie_id_filter)
        
        return queryset.order_by('-created_at')


# Views alternativas (caso prefira usar views separadas ao invés de actions)
class MinhasReservasView(generics.ListAPIView):
    """API View alternativa para listar reservas do usuário"""
    serializer_class = TicketReservationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return TicketReservation.objects.filter(user=self.request.user).order_by('-created_at')


class EstatisticasReservasView(APIView):
    """API View alternativa para estatísticas das reservas"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        if user.is_admin_user():
            # Estatísticas gerais para administradores
            total_reservas = TicketReservation.objects.count()
            reservas_pendentes = TicketReservation.objects.filter(status='pending').count()
            reservas_confirmadas = TicketReservation.objects.filter(status='confirmed').count()
            reservas_canceladas = TicketReservation.objects.filter(status='cancelled').count()
            reservas_concluidas = TicketReservation.objects.filter(status='completed').count()
        else:
            # Estatísticas do usuário específico
            total_reservas = TicketReservation.objects.filter(user=user).count()
            reservas_pendentes = TicketReservation.objects.filter(user=user, status='pending').count()
            reservas_confirmadas = TicketReservation.objects.filter(user=user, status='confirmed').count()
            reservas_canceladas = TicketReservation.objects.filter(user=user, status='cancelled').count()
            reservas_concluidas = TicketReservation.objects.filter(user=user, status='completed').count()
        
        return Response({
            'total_reservas': total_reservas,
            'reservas_pendentes': reservas_pendentes,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_canceladas': reservas_canceladas,
            'reservas_concluidas': reservas_concluidas
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def minhas_reservas(self, request):
        """Endpoint para o usuário ver suas próprias reservas"""
        reservas = TicketReservation.objects.filter(user=request.user).order_by('-created_at')
        serializer = self.get_serializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['patch'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin])
    def update_status(self, request, pk=None):
        """Endpoint para atualizar apenas o status da reserva"""
        reserva = self.get_object()
        serializer = TicketReservationUpdateStatusSerializer(
            reserva, 
            data=request.data, 
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Retornar dados completos da reserva após atualização
        full_serializer = TicketReservationSerializer(reserva)
        return Response(full_serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOwnerOrAdmin])
    def cancelar(self, request, pk=None):
        """Endpoint para cancelar uma reserva"""
        reserva = self.get_object()
        
        if not reserva.can_be_cancelled():
            return Response(
                {'error': 'Esta reserva não pode ser cancelada.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.status = 'cancelled'
        reserva.save()
        
        serializer = self.get_serializer(reserva)
        return Response({
            'message': 'Reserva cancelada com sucesso.',
            'reserva': serializer.data
        })
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def estatisticas(self, request):
        """Endpoint para estatísticas das reservas do usuário"""
        user = request.user
        
        if user.is_admin_user():
            # Estatísticas gerais para administradores
            total_reservas = TicketReservation.objects.count()
            reservas_pendentes = TicketReservation.objects.filter(status='pending').count()
            reservas_confirmadas = TicketReservation.objects.filter(status='confirmed').count()
            reservas_canceladas = TicketReservation.objects.filter(status='cancelled').count()
            reservas_concluidas = TicketReservation.objects.filter(status='completed').count()
        else:
            # Estatísticas do usuário específico
            total_reservas = TicketReservation.objects.filter(user=user).count()
            reservas_pendentes = TicketReservation.objects.filter(user=user, status='pending').count()
            reservas_confirmadas = TicketReservation.objects.filter(user=user, status='confirmed').count()
            reservas_canceladas = TicketReservation.objects.filter(user=user, status='cancelled').count()
            reservas_concluidas = TicketReservation.objects.filter(user=user, status='completed').count()
        
        return Response({
            'total_reservas': total_reservas,
            'reservas_pendentes': reservas_pendentes,
            'reservas_confirmadas': reservas_confirmadas,
            'reservas_canceladas': reservas_canceladas,
            'reservas_concluidas': reservas_concluidas
        })


class TicketReservationPublicViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para visualização pública de reservas (dados limitados)"""
    queryset = TicketReservation.objects.filter(status__in=['confirmed', 'completed'])
    serializer_class = TicketReservationPublicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Permitir busca por filme"""
        queryset = super().get_queryset()
        movie_id = self.request.query_params.get('movie_id', None)
        
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        
        return queryset.order_by('-created_at')