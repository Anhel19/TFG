from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'role', 'is_staff', 'created_at')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)

    # Añadimos los campos personalizados al formulario de edición
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Información adicional', {'fields': ('phone', 'role')}),
    )
