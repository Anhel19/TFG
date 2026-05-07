from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsReservationOwnerOrRestaurantOwner

from .models import Reservation
from .serializers import (
    ReservationCreateSerializer,
    ReservationDetailSerializer,
    ReservationListSerializer,
)


class ReservationViewSet(viewsets.ModelViewSet):
    """
    CRUD de reservas.
    - Crear: cualquiera (autenticado o invitado)
    - Listar/ver/cancelar: solo el cliente o el dueño del restaurante
    """
    queryset = Reservation.objects.select_related('restaurant', 'table', 'user')

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservationListSerializer
        if self.action == 'create':
            return ReservationCreateSerializer
        return ReservationDetailSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ['list']:
            return [permissions.IsAuthenticated()]
        # retrieve, update, destroy, cancel
        return [permissions.IsAuthenticated(), IsReservationOwnerOrRestaurantOwner()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Reservation.objects.none()

        qs = Reservation.objects.select_related('restaurant', 'table', 'user')

        if user.is_staff:
            return qs

        # Filtro: el cliente ve sus reservas + el owner ve las de sus restaurantes
        from django.db.models import Q
        return qs.filter(
            Q(user=user) | Q(restaurant__owner=user)
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """POST /api/reservations/{id}/cancel/ → cancelar reserva."""
        reservation = self.get_object()

        if reservation.status == Reservation.Status.CANCELLED:
            return Response(
                {'detail': 'La reserva ya estaba cancelada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=['status', 'updated_at'])
        return Response(
            ReservationDetailSerializer(reservation).data,
            status=status.HTTP_200_OK,
        )