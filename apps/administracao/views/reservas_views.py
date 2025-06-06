from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from apps.reservas.models import TicketReservation
from django.contrib.auth import get_user_model
User = get_user_model()
import json

class TicketReservationListView(LoginRequiredMixin, ListView):
    model = TicketReservation
    template_name = 'administracao/reservas/listarReservas.html'
    context_object_name = 'reservas'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtro de pesquisa
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(user__identification_number__icontains=search_query) |
                Q(movie_id__icontains=search_query) |
                Q(session__icontains=search_query)
            )
        
        # Filtro por status
        status = self.request.GET.get('status', '')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filtro por usuário
        user_id = self.request.GET.get('user_id', '')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filtro por data
        date_from = self.request.GET.get('date_from', '')
        date_to = self.request.GET.get('date_to', '')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Adicionar filtros no contexto
        context['search_query'] = self.request.GET.get('search', '')
        context['status_selected'] = self.request.GET.get('status', '')
        context['user_id_selected'] = self.request.GET.get('user_id', '')
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        
        # Adicionar choices de status
        context['status_choices'] = TicketReservation.STATUS_CHOICES
        
        # Adicionar usuários para o filtro
        context['usuarios'] = User.objects.filter(is_active=True).order_by('full_name')
        
        return context


class TicketReservationDetailView(LoginRequiredMixin, DetailView):
    model = TicketReservation
    template_name = 'administracao/reservas/detalhes.html'
    context_object_name = 'reserva'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Processar assentos se estiver em formato JSON
        try:
            import json
            seats_data = json.loads(self.object.seats)
            context['seats_list'] = seats_data if isinstance(seats_data, list) else [seats_data]
        except (json.JSONDecodeError, ValueError):
            # Se não for JSON válido, tratar como string
            context['seats_list'] = self.object.seats.split(',') if self.object.seats else []
        
        return context


class TicketReservationUpdateStatusView(LoginRequiredMixin, View):
    """View para atualizar status da reserva via AJAX"""
    
    def post(self, request, pk):
        try:
            reserva = get_object_or_404(TicketReservation, pk=pk)
            new_status = request.POST.get('status')
            
            if new_status in dict(TicketReservation.STATUS_CHOICES):
                reserva.status = new_status
                reserva.save()
                
                return JsonResponse({
                    'success': True,
                    'message': f'Status da reserva alterado para {reserva.get_status_display()}',
                    'new_status': new_status,
                    'new_status_display': reserva.get_status_display()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Status inválido'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao atualizar status: {str(e)}'
            })