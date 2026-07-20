from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import ListingForm
from .models import Listing
from .utils import calculate_service_fee
from .decorators import provider_verified_required

@login_required
def create_listing(request):
    # 1. Role Check
    if request.user.role != "provider":
        messages.error(request, "Only providers can create listings.")
        return redirect("dashboard:dashboard")

    # 2. Verification Check (admin approval required)
    if not request.user.is_verified:
        messages.error(request, "Your account is awaiting admin approval before you can post listings.")
        return redirect("dashboard:dashboard")

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.is_active = False   # ✅ keep inactive until payment confirmed
            listing.save()

            # 3. Dynamic Fee Calculation (per post)
            fee = calculate_service_fee(listing.price, listing.category)
            request.session["calculated_fee"] = float(fee)

            # 🚨 Reset provider payment status until admin confirms
            request.user.is_paid = False
            request.user.save()

            messages.info(request, "Listing saved in pending state. Please complete payment.")
            return redirect("accounts:payment_gateway", listing_id=listing.id)
    else:
        form = ListingForm()

    return render(request, "listings/create_listing.html", {"form": form})

def list_listings(request):
    query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    listings = Listing.objects.all().order_by('-is_featured', '-created_at') # Featured first

    if query:
        listings = listings.filter(product_name__icontains=query)
    if min_price:
        listings = listings.filter(price__gte=min_price)
        
    return render(request, 'listings/list.html', {'listings': listings})

def support_view(request):
    return render(request, 'listings/support.html')

def terms_view(request):
    return render(request, 'listings/terms.html')

def about_view(request):
    return render(request, 'listings/about.html')

from django.shortcuts import render, get_object_or_404
from .models import Listing

@login_required
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)

    # Increment views
    listing.views = (listing.views or 0) + 1
    listing.save(update_fields=["views"])

    return render(request, "listings/detail.html", {"listing": listing})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Listing, Booking

@login_required
def create_booking(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    provider = listing.user

    if request.method == "POST":
        request_type = request.POST.get("request_type")
        customer_message = request.POST.get("customer_message", "")

        Booking.objects.create(
            listing=listing,
            customer=request.user,
            provider=provider,
            request_type=request_type,
            customer_message=customer_message,
        )

        messages.success(request, f"{request_type.capitalize()} request sent to {provider.username}.")
        return redirect("listings:listing_detail", pk=listing.pk)

    return render(request, "listings/create_booking.html", {"listing": listing})


@login_required
def provider_bookings(request):
    # Get all bookings for listings owned by the logged-in provider
    bookings = Booking.objects.filter(listing__user=request.user).order_by("-created_at")
    return render(request, "listings/provider_bookings.html", {"bookings": bookings})

from dashboard.models import AuditLog

@login_required
def respond_to_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, listing__user=request.user)

    if request.method == "POST":
        status = request.POST.get("status")
        response_text = request.POST.get("response")

        if status not in ["accepted", "rejected"]:
            messages.error(request, "Invalid status choice.")
            return redirect("provider_bookings")

        booking.status = status
        booking.provider_response = response_text
        booking.save()

        # Optional: log provider action
        AuditLog.objects.create(
            actor=request.user,
            action=f"Provider {status} booking",
            target_user=booking.customer,
        )

        messages.success(request, "Response sent successfully!")
        return redirect("provider_bookings")

    return render(request, "listings/respond.html", {"booking": booking})



# listings/views.py
from django.shortcuts import render
from django.utils import timezone   # 👈 Needed for featured_until
from .models import Listing

def marketplace(request):
    q = request.GET.get('q')
    category = request.GET.get('category')
    sort = request.GET.get('sort')
    
    # ✅ Only define featured_listings once
    featured_listings = Listing.objects.filter(
        is_active=True,
        is_featured=True,
        featured_until__gte=timezone.now()   # 👈 Only show listings still within promo period
    ).order_by('-created_at')[:5]

    # Regular listings
    listings = Listing.objects.filter(is_active=True)

    if q:
        listings = listings.filter(title__icontains=q)

    if category:
        listings = listings.filter(category=category)

    if sort == 'price_low':
        listings = listings.order_by('price')
    elif sort == 'price_high':
        listings = listings.order_by('-price')
    elif sort == 'recent':
        listings = listings.order_by('-created_at')

    return render(request, 'listings/marketplace.html', {
        'listings': listings,
        'featured_listings': featured_listings,
        'categories': Listing.CATEGORY_CHOICES
    })
# listings/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Listing

def complete_payment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    fee = 5.00  # Example fee
    ecocash_number = "0771234567"

    if request.method == "POST":
        transaction_ref = request.POST.get("transaction_ref")

        # Simulated verification: accept any non-empty reference
        if transaction_ref and len(transaction_ref) >= 6:
            listing.is_featured = True
            listing.featured_until = timezone.now() + timedelta(days=7)  # 👈 Featured for 7 days
            listing.save()

            # Redirect to dashboard with success message
            return redirect("dashboard")

        else:
            # Simulated failure
            return render(request, "listings/complete_payment.html", {
                "listing": listing,
                "fee": fee,
                "ecocash_number": ecocash_number,
                "error": "Invalid transaction reference. Please try again."
            })

    return render(request, "listings/complete_payment.html", {
        "listing": listing,
        "fee": fee,
        "ecocash_number": ecocash_number
    })


def support_ticket_view(request):
    # handle form submission or show ticket form
    return render(request, 'listings/support.html')


def feedback(request):
    # handle form submission or show ticket form
    return render(request, 'listings/support.html')

# marketplace/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Listing, Review
from django.contrib.auth.decorators import login_required

@login_required
def add_review(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        rating = int(request.POST.get("rating", 1))
        comment = request.POST.get("comment", "")
        
        if request.user != listing.user:
         Review.objects.create(
            listing=listing,
            user=request.user,
            rating=rating,
            comment=comment
        )
        return redirect("listing_detail.html", listing_id=listing.id)

from django.db.models import Avg
from django.db.models import Avg
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

@login_required
def listing_detail(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    # Increment views safely
    listing.views = (listing.views or 0) + 1
    listing.save(update_fields=["views"])

    # Reviews and average rating
    reviews = listing.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if avg_rating:
        avg_rating = round(avg_rating, 1)

    context = {
        'listing': listing,
        'avg_rating': avg_rating,
    }
    return render(request, 'listings/listing_detail.html', context)

@login_required
def edit_listing(request, pk):
    # Ensure only the owner can edit
    listing = get_object_or_404(Listing, pk=pk, user=request.user)

    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Listing updated successfully.")
            return redirect("listings:listing_detail", pk=listing.pk)
    else:
        form = ListingForm(instance=listing)

    return render(request, "listings/edit_listing.html", {"form": form, "listing": listing})


@login_required
def delete_listing(request, pk):
    # Ensure only the owner can delete
    listing = get_object_or_404(Listing, pk=pk, user=request.user)

    if request.method == "POST":
        listing.delete()
        messages.success(request, "Listing deleted successfully.")
        return redirect("listings:list_listings")  # or "dashboard:dashboard" if you prefer

    # GET → show confirmation page
    return render(request, "listings/confirm.html", {"listing": listing})


@login_required
def provider_listings(request):
    # Get all listings created by the logged‑in provider
    listings = request.user.listings.all().order_by("-created_at")
    return render(request, "listings/provider_listings.html", {"listings": listings})


