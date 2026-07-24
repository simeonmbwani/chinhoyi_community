from rest_framework import serializers
from .models import Listing, Booking

class ListingSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    average_rating = serializers.ReadOnlyField()

    class Meta:
        model = Listing
        fields = [
            'id', 'username', 'product_name', 'description', 
            'category', 'price', 'location', 'image', 
            'is_active', 'status', 'created_at', 'views', 'average_rating'
        ]