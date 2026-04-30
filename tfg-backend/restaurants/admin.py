from django.contrib import admin
from .models import Restaurant


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner', 'capacity', 'is_active', 'created_at')
    list_filter = ('is_active', 'city')
    search_fields = ('name', 'city', 'address', 'owner__email')
    ordering = ('-created_at',)