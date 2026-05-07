from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from users.permissions import IsOwnerRole, IsRestaurantOwner

from .models import OpeningHours, Restaurant, Table
from .serializers import (
    OpeningHoursSerializer,
    RestaurantDetailSerializer,
    RestaurantListSerializer,
    RestaurantWriteSerializer,
    TableSerializer,
)


class RestaurantViewSet(viewsets.ModelViewSet):
    """
    CRUD de restaurantes.
    - Listar/ver: público
    - Crear: solo OWNER autenticado
    - Editar/borrar: solo dueño del restaurante o staff
    """
    queryset = Restaurant.objects.filter(is_active=True).select_related('owner')

    def get_serializer_class(self):
        if self.action == 'list':
            return RestaurantListSerializer
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantWriteSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsOwnerRole()]
        # update, partial_update, destroy
        return [permissions.IsAuthenticated(), IsRestaurantOwner()]

    def get_queryset(self):
        qs = Restaurant.objects.select_related('owner')
        # En el listado público solo restaurantes activos
        if self.action == 'list' and not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        # Filtros opcionales por query params
        city = self.request.query_params.get('city')
        if city:
            qs = qs.filter(city__icontains=city)
        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """GET /api/restaurants/mine/ → restaurantes del usuario autenticado."""
        qs = Restaurant.objects.filter(owner=request.user)
        serializer = RestaurantListSerializer(qs, many=True)
        return Response(serializer.data)


class TableViewSet(viewsets.ModelViewSet):
    """CRUD de mesas. Solo el dueño del restaurante puede gestionarlas."""
    serializer_class = TableSerializer
    queryset = Table.objects.select_related('restaurant')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsRestaurantOwner()]

    def get_queryset(self):
        qs = Table.objects.select_related('restaurant')
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs


class OpeningHoursViewSet(viewsets.ModelViewSet):
    """CRUD de horarios de apertura. Solo el dueño puede gestionarlos."""
    serializer_class = OpeningHoursSerializer
    queryset = OpeningHours.objects.select_related('restaurant')

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsRestaurantOwner()]

    def get_queryset(self):
        qs = OpeningHours.objects.select_related('restaurant')
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)
        return qs