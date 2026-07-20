from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Payment

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # This ensures we don't double-include fields
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'is_verified', 'id_document', 'profile_picture', 'bio', 'phone_number', 'business_name')}),
    )
    list_display = ['username', 'role', 'is_verified', 'business_name']
    list_editable = ['is_verified']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'is_confirmed', 'created_at']
    list_editable = ['is_confirmed']
