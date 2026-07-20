from django.contrib import admin
from .models import Listing, Booking, Favorite

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'user', 'category', 'price', 'location', 'is_active', 'is_featured', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'location')
    search_fields = ('title', 'description', 'user__username')
    list_editable = ('is_active', 'is_featured')  # 👈 Quick toggle in admin list view

def approve_listing_payment(modeladmin, request, queryset):
    for listing in queryset:
        listing.is_active = True
        listing.user.is_paid = True
        listing.save()
approve_listing_payment.short_description = "Mark selected listings as paid & activate"
