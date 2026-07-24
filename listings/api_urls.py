from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, FavoriteViewSet, ReviewViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listings')
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = router.urls
