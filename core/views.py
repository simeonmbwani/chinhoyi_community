from django.shortcuts import render
from listings.models import Listing

def landing_page(request):
    # Fetch only the latest 6 active listings for the front page
    listings = Listing.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, 'core/landing.html', {'listings': listings})
