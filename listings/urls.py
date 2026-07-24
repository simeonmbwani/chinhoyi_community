from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, FavoriteViewSet, ReviewViewSet, FeedbackViewSet

app_name = "listings"

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listings')
router.register(r'bookings', BookingViewSet, basename='bookings')
router.register(r'favorites', FavoriteViewSet, basename='favorites')
router.register(r'reviews', ReviewViewSet, basename='reviews')
router.register(r'feedback', FeedbackViewSet, basename='feedback')

urlpatterns = [
    # General & Marketplace
    path("", views.list_listings, name="list_listings"),
    path("latest/", views.latest_listings, name="latest"),

    # JWT Auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Creation
    path("create/", views.create_listing, name="create_listing"),
    path("new/", views.create_listing, name="create_listing"),

    # Detail & Management
    path("<int:pk>/", views.listing_detail, name="listing_detail"),
    path("<int:listing_id>/edit/", views.edit_listing, name="edit_listing"),
    path("edit/<int:pk>/", views.edit_listing, name="edit_listing"),
    path("delete/<int:pk>/", views.delete_listing, name="delete_listing"),

    # Provider Portal
    path("provider/listings/", views.provider_listings, name="provider_listings"),
    path("provider/bookings/", views.provider_bookings, name="provider_bookings"),
    path("provider/bookings/<int:booking_id>/respond/", views.respond_to_booking, name="respond_to_booking"),

    # Bookings (Customer)
    path("booking/create/<int:pk>/", views.create_booking, name="create_booking"),

    # Support & Feedback
    path("support/", views.support_view, name="support"),
    path("support/ticket/", views.support_ticket_view, name="support_ticket"),
    path("support/feedback/", views.support_ticket_view, name="feedback"),
    path("feedback/", views.feedback, name="feedback_form"),

    # Static Pages
    path("terms/", views.terms_view, name="terms"),
    path("about/", views.about_view, name="about"),

    # API endpoints (DRF router)
    path("api/", include(router.urls)),
]
