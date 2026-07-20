from django.urls import path
from . import views
from django.shortcuts import render

app_name = "listings"

urlpatterns = [
    path("", views.list_listings, name="list_listings"),
    path('create/', views.create_listing, name='create_listing'),
    path('new/', views.create_listing, name='create_listing'),

    # Listing detail
    path('<int:pk>/', views.listing_detail, name='listing_detail'),
    
    # Payments
    # Static pages
    path('support/', views.support_view, name='support'),
    path('terms/', views.terms_view, name='terms'),
    path('about/', views.about_view, name='about'),

    # Bookings
    path('booking/create/<int:pk>/', views.create_booking, name='create_booking'),
    path('provider/bookings/', views.provider_bookings, name='provider_bookings'),
    path("provider/bookings/<int:booking_id>/respond/", views.respond_to_booking, name="respond_to_booking"),
    path("provider/listings/", views.provider_listings, name="provider_listings"),


    # Listing management
  
    path("<int:listing_id>/edit/", views.edit_listing, name="edit_listing"),
    path('edit/<int:pk>/', views.edit_listing, name='edit_listing'),
    path('delete/<int:pk>/', views.delete_listing, name='delete_listing'),

    # Support
    path('support/ticket/', views.support_ticket_view, name='support_ticket'),
    path('support/feedback/', views.support_ticket_view, name='feedback'),
    path("provider/bookings/", views.provider_bookings, name="provider_bookings")

]
