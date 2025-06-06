# apps/reservas/api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TicketReservationViewSet,
    TicketReservationPublicViewSet,
    MinhasReservasView,
    EstatisticasReservasView
)

router = DefaultRouter()
router.register('reservas', TicketReservationViewSet, basename='reserva')
router.register('reservas-publico', TicketReservationPublicViewSet, basename='reserva-publico')

app_name = 'api_reservas'

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs customizadas adicionais (se preferir usar views separadas)
    path('minhas-reservas/', MinhasReservasView.as_view(), name='minhas-reservas'),
    path('estatisticas/', EstatisticasReservasView.as_view(), name='estatisticas'),
    
    # URLs específicas para ações do ViewSet (geradas automaticamente pelo router)
    # GET/POST /reservas/ - listar/criar reservas
    # GET/PUT/PATCH/DELETE /reservas/{id}/ - operações específicas
    # GET /reservas/minhas_reservas/ - minhas reservas (action do ViewSet)
    # PATCH /reservas/{id}/update_status/ - atualizar status (action do ViewSet)
    # POST /reservas/{id}/cancelar/ - cancelar reserva (action do ViewSet)
    # GET /reservas/estatisticas/ - estatísticas (action do ViewSet)
    # GET /reservas-publico/ - reservas públicas
    # GET /reservas-publico/{id}/ - reserva pública específica
]