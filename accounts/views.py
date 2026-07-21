from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import UserRegistrationForm, ProfileEditForm, ReviewForm
from .models import Wallet
from django.utils import timezone
from listings.models import Listing
from .models import Transaction

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            # Providers must be verified manually, buyers auto-verified
            user.is_verified = (user.role != 'provider')
            user.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")

            # ✅ No payment redirect here — all users go to dashboard
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # Explicitly return the dashboard URL
        return reverse_lazy('dashboard:dashboard')


# --- Profile Management ---
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})

# --- Wallet & Reviews ---
@login_required
def wallet_view(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-timestamp')
    return render(request, 'accounts/wallet.html', {
        'wallet': wallet,
        'transactions': transactions
    })
from listings.models import Listing

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .forms import ReviewForm
from listings.models import Listing

from django.http import JsonResponse

@login_required
def add_review(request, pk):
    listing_obj = get_object_or_404(Listing, pk=pk)
    provider = listing_obj.user

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.listing = listing_obj
            review.reviewer = request.user
            review.provider = provider
            review.save()

            return JsonResponse({
                "success": True,
                "reviewer": request.user.username,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.strftime("%b %d, %Y %H:%M"),
            })
        else:
            return JsonResponse({"success": False, "error": "Invalid form"})
    return JsonResponse({"success": False, "error": "Invalid request"})

from decimal import Decimal

@login_required
def payment_gateway(request, listing_id=None):
    listing = None
    if listing_id:
        listing = get_object_or_404(Listing, id=listing_id, user=request.user)

    # Define service fee (fixed or percentage)
    service_fee = Decimal("2.50")  # flat fee
    if listing:
        listing_price = listing.price
        amount = listing_price + service_fee
    else:
        listing_price = Decimal("0.00")
        amount = service_fee

    ECOCASH_NUMBER = "+263775493710"  # move to settings/env later

    if request.method == "POST":
        transaction_ref = request.POST.get("transaction_ref")

        if transaction_ref:
            # ✅ Save transaction record with valid fields only
            Transaction.objects.create(
                user=request.user,
                listing=listing,
                amount=amount,
                service_fee=service_fee,
                transaction_type="payment",
                status="success",          # valid field
                reference=transaction_ref  # valid field
                # timestamp is auto_now_add, so no need for payment_date
            )

            # ✅ Mark provider as paid
            request.user.is_paid = True
            request.user.save(update_fields=["is_paid"])

            # ✅ If tied to a listing, mark payment done but keep inactive until admin approves
            if listing:
                listing.payment_reference = transaction_ref
                listing.payment_date = timezone.now()
                listing.payment_status = "paid"          # clearer than "completed"
                listing.is_active = False                # inactive until admin approves
                listing.status = "awaiting_approval"     # distinguish from unpaid
                listing.save(update_fields=[
                    "payment_reference", "payment_date", "payment_status", "is_active", "status"
                ])

            messages.success(
                request,
                f"Payment of ${amount} recorded successfully (Ref: {transaction_ref}). "
                + ("Awaiting admin approval before your listing goes live." if listing else "Your provider account is now active.")
            )
            return redirect("dashboard:dashboard")
        else:
            messages.error(request, "Please enter your EcoCash Reference ID to proceed.")

    context = {
        "listing": listing,
        "listing_price": listing_price,
        "service_fee": service_fee,
        "amount": amount,
        "ecocash_number": ECOCASH_NUMBER,
    }
    return render(request, "accounts/payment.html", context)


from decimal import Decimal
from django.utils import timezone
from .models import Wallet, Transaction

@login_required
def wallet_topup(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    ECOCASH_NUMBER = "+263775493710"  # move to settings/env later
    service_fee = Decimal("0.50")     # example fee for top‑up

    if request.method == "POST":
        amount = Decimal(request.POST.get("amount", "0"))
        transaction_ref = request.POST.get("transaction_ref")

        if amount > 0 and transaction_ref:
            # ✅ Record transaction
            Transaction.objects.create(
                user=request.user,
                wallet=wallet,
                amount=amount,
                service_fee=service_fee,
                transaction_type="deposit",
                status="success",
                reference=transaction_ref
            )

            # ✅ Update wallet balance
            wallet.balance += amount
            wallet.save(update_fields=["balance"])

            messages.success(
                request,
                f"Wallet topped up with ${amount} (Ref: {transaction_ref})."
            )
            return redirect("accounts:wallet")
        else:
            messages.error(request, "Please enter a valid amount and EcoCash Reference ID.")

    context = {
        "wallet": wallet,
        "ecocash_number": ECOCASH_NUMBER,
    }
    return render(request, "accounts/wallet_topup.html", context)
