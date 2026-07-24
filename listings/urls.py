from django.urls import path
from . import views
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

app_name = "listings"

urlpatterns = [
    # General & Marketplace
    path("", views.list_listings, name="list_listings"),
    path("latest/", views.latest_listings, name="latest"),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Feature Endpoints
    path('api/', include('listings.api_urls')),
    path('api/messaging/', include('messaging.api_urls')),
    
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
]