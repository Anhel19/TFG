from django.contrib import admin
from .models import Restaurant, Table, OpeningHours


class TableInline(admin.TabularInline):
    model = Table
    extra = 1


class OpeningHoursInline(admin.TabularInline):
    model = OpeningHours
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'city']
    search_fields = ['name', 'city', 'address']
    inlines = [TableInline, OpeningHoursInline]


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'number', 'capacity', 'is_active']
    list_filter = ['restaurant', 'is_active']


@admin.register(OpeningHours)
class OpeningHoursAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'day_of_week', 'opening_time', 'closing_time']
    list_filter = ['restaurant', 'day_of_week']