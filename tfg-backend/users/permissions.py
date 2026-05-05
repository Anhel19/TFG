from rest_framework import permissions


class IsAdminRole(permissions.BasePermission):
    """Permite solo a usuarios con role=ADMIN."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'ADMIN'
        )


class IsStaffOrAdmin(permissions.BasePermission):
    """Permite a STAFF y ADMIN."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['STAFF', 'ADMIN']
        )


class IsOwnerOrStaff(permissions.BasePermission):
    """
    Para reservas: el cliente solo accede a las suyas;
    staff/admin acceden a todas.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['STAFF', 'ADMIN']:
            return True
        return obj.user == request.user