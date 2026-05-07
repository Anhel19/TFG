from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OpeningHoursViewSet, RestaurantViewSet, TableViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'opening-hours', OpeningHoursViewSet, basename='openinghours')

urlpatterns = [
    path('', include(router.urls)),
]