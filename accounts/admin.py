from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Wallet, Transaction, AuditLog, Notification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': (
                'role',
                'is_verified',
                'id_document',
                'profile_picture',
                'bio',
                'phone_number',
                'business_name'
            )
        }),
    )
    list_display = ['username', 'role', 'is_verified', 'business_name']
    list_editable = ['is_verified']


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'transaction_type', 'status', 'timestamp']
    list_editable = ['status']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['actor', 'action', 'target_user', 'timestamp']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'timestamp']
    list_editable = ['is_read']
