from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'guest_name',
        'restaurant',
        'reservation_datetime',
        'party_size',
        'status',
        'is_guest_reservation',
    )
    list_filter = ('status', 'restaurant', 'reservation_datetime')
    search_fields = ('guest_name', 'guest_email', 'guest_phone', 'restaurant__name')
    date_hierarchy = 'reservation_datetime'
    ordering = ('-reservation_datetime',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Restaurante y cliente', {
            'fields': ('restaurant', 'user', 'guest_name', 'guest_email', 'guest_phone'),
        }),
        ('Detalles de la reserva', {
            'fields': ('reservation_datetime', 'party_size', 'notes', 'status'),
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(boolean=True, description='Invitado')
    def is_guest_reservation(self, obj):
        return obj.is_guest_reservation
