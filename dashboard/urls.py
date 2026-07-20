from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # User dashboards
    path("", views.user_dashboard, name="dashboard"), 

    # Admin main dashboard + stats
    path("admin-dashboard-stats/", views.admin_dashboard_stats, name="admin_dashboard_stats"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),

    # HTMX partials
    path("admin/users/partial/", views.admin_users_partial, name="admin_users_partial"),
    path("admin/logs/partial/", views.admin_logs_partial, name="admin_logs_partial"),

    # Verification modal + actions
    path("admin/user/<int:user_id>/verification/", views.admin_user_verification_partial, name="admin_user_verification_partial"),
    path("admin/user/<int:user_id>/<str:action>/", views.admin_manage_user, name="admin_manage_user"),
     
    path("admin/listings/partial/", views.admin_listings_partial, name="admin_listings_partial"),
    path("admin/bookings/partial/", views.admin_bookings_partial, name="admin_bookings_partial"),
    path("admin/listing/<int:listing_id>/<str:action>/", views.admin_manage_listing, name="admin_manage_listing"),
    path("admin/booking/<int:booking_id>/<str:action>/", views.admin_manage_booking, name="admin_manage_booking"),
    path("cancel/<int:booking_id>/", views.cancel_booking, name="cancel_booking"), 

    path("notifications/partial/", views.notifications_partial, name="notifications_partial"),
    path("wallet/partial/", views.wallet_partial, name="wallet_partial"),
    path("provider/stats/", views.provider_stats_partial, name="provider_stats_partial"),
    path("buyer/stats/", views.buyer_stats_partial, name="buyer_stats_partial"),
    path("messages/partial/", views.messages_partial, name="messages_partial"),
    path("bookings/all/", views.all_bookings, name="all_bookings"),
    path("provider/bookings/", views.provider_bookings, name="provider_bookings"),
    path("provider/reviews/", views.provider_reviews, name="provider_reviews"),
    path("chats/", views.dashboard_chats, name="dashboard_chats"),
    path("transactions-partial/", views.admin_transactions_partial, name="admin_transactions_partial"), 
]




