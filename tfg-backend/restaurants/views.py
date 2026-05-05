from datetime import datetime

from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Restaurant, Table, OpeningHours
from .serializers import (
    RestaurantListSerializer,
    RestaurantDetailSerializer,
    TableSerializer,
    OpeningHoursSerializer,
)
from reservations.availability import get_available_slots


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    CRUD de restaurantes.
    - list / retrieve / availability  -> público
    - create / update / destroy       -> solo admin/staff
    """
    queryset = Restaurant.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantListSerializer
        return RestaurantDetailSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'availability'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def availability(self, request, pk=None):
        """
        GET /api/restaurants/{id}/availability/?date=YYYY-MM-DD&guests=N
        Devuelve los slots horarios disponibles para esa fecha y nº de comensales.
        """
        restaurant = self.get_object()
        date_str = request.query_params.get('date')
        guests_str = request.query_params.get('guests')

        if not date_str or not guests_str:
            return Response(
                {'detail': 'Parámetros requeridos: date (YYYY-MM-DD) y guests.'},
                status=400,
            )
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            guests = int(guests_str)
        except ValueError:
            return Response({'detail': 'Formato inválido.'}, status=400)

        slots = get_available_slots(restaurant, date, guests)
        return Response({'date': date_str, 'guests': guests, 'slots': slots})


class TableViewSet(viewsets.ModelViewSet):
    """CRUD de mesas."""
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]


class OpeningHoursViewSet(viewsets.ModelViewSet):
    """CRUD de horarios."""
    queryset = OpeningHours.objects.all()
    serializer_class = OpeningHoursSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]