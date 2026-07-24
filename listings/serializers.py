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
        
from rest_framework import serializers
from .models import Listing, Booking, Favorite, Review, Feedback

class ListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = "__all__"

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = "__all__"

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = "__all__"

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = "__all__"
        