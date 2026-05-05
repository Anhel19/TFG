from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Reservation
from .serializers import ReservationSerializer
from .permissions import IsCustomerOrAnonymousCreate, IsOwnerOrStaff


class ReservationViewSet(viewsets.ModelViewSet):
    """
    Reservas:
    - create: CUSTOMER autenticado o invitado anónimo
    - list/retrieve/update/destroy: solo el dueño o staff
    - cancel: cambia el estado a CANCELLED
    """
    serializer_class = ReservationSerializer
    permission_classes = [IsCustomerOrAnonymousCreate, IsOwnerOrStaff]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Reservation.objects.none()
        if user.is_staff:
            return Reservation.objects.all()
        return Reservation.objects.filter(user=user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status == Reservation.Status.CANCELLED:
            return Response(
                {'detail': 'La reserva ya estaba cancelada.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation.status = Reservation.Status.CANCELLED
        reservation.save()
        return Response(self.get_serializer(reservation).data)