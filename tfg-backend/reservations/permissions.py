from rest_framework import permissions

from users.models import User


class IsCustomerOrAnonymousCreate(permissions.BasePermission):
    """
    - Crear: cualquier usuario CUSTOMER autenticado, o anónimo (invitado).
    - Listar/leer/editar/borrar: solo autenticados (filtrado por dueño en el viewset).
    """
    def has_permission(self, request, view):
        if view.action == 'create':
            if request.user.is_authenticated:
                return getattr(request.user, 'role', None) == User.Role.CUSTOMER
            return True  # invitado puede crear
        return request.user and request.user.is_authenticated


class IsOwnerOrStaff(permissions.BasePermission):
    """Solo el usuario dueño de la reserva o staff puede ver/modificar."""
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.user_id == request.user.id