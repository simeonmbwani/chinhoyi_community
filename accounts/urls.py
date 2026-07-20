from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.shortcuts import render

app_name = "accounts"

urlpatterns = [
    # --- Auth & Registration ---
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='accounts:login'), name='logout'),

    # --- Profile (Identity & Settings) ---
    # Strictly for viewing identity and editing account info
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # --- Wallet & Reviews ---
    path('wallet/', views.wallet_view, name='wallet'),
    path("wallet/topup/", views.wallet_topup, name="wallet_topup"),
    path("review/<int:pk>/", views.add_review, name="add_review"),
    path("payment/", views.payment_gateway, name="payment_gateway"),
    path("payment/<int:listing_id>/", views.payment_gateway, name="payment_gateway_with_listing"),
    path("payment/<int:listing_id>/", views.payment_gateway, name="payment_gateway"),
    path('payment/success/', lambda request: render(request, 'listings/success.html'), name='payment_success'),

    
    # --- Password Reset ---
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]