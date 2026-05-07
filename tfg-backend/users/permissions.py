from rest_framework import permissions

from .models import User


class IsOwnerRole(permissions.BasePermission):
    """Permite acceso solo a usuarios con role=OWNER (o staff)."""
    message = 'Solo los dueños de restaurante pueden hacer esto.'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_staff or request.user.role == User.Role.OWNER


class IsRestaurantOwner(permissions.BasePermission):
    """
    Permite acceso solo si el usuario es el dueño del restaurante
    relacionado con el objeto. Funciona para Restaurant, Table y OpeningHours.
    """
    message = 'No tienes permiso sobre este restaurante.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # obj puede ser Restaurant, Table o OpeningHours
        if hasattr(obj, 'owner_id'):
            return obj.owner_id == request.user.id
        if hasattr(obj, 'restaurant'):
            return obj.restaurant.owner_id == request.user.id
        return False


class IsReservationOwnerOrRestaurantOwner(permissions.BasePermission):
    """
    Para reservas: el cliente solo ve/edita las suyas; el dueño del
    restaurante ve/edita las de su restaurante; el staff ve todo.
    """
    message = 'No tienes acceso a esta reserva.'

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        # Cliente dueño de la reserva
        if obj.user_id and obj.user_id == request.user.id:
            return True
        # Dueño del restaurante donde se hizo la reserva
        if obj.restaurant.owner_id == request.user.id:
            return True
        return False


class IsReadOnly(permissions.BasePermission):
    """Permite solo métodos seguros (GET, HEAD, OPTIONS)."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS