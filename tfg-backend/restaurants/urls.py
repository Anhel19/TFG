from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, TableViewSet, OpeningHoursViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'tables', TableViewSet, basename='table')
router.register(r'opening-hours', OpeningHoursViewSet, basename='openinghours')

urlpatterns = router.urls