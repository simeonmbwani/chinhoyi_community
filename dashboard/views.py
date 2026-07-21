from django.shortcuts import render, get_object_or_404,redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import CustomUser, Wallet
from dashboard.models import AuditLog   # <-- keep AuditLog in dashboard app
from listings.models import Listing, Booking
from accounts.models import Notification
from django.db.models import Q
from messaging.models import Message, ChatRoom


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    booking.status = "cancelled"   # adjust to your model’s status field
    booking.save()
    return redirect("dashboard:dashboard")   # back to user dashboard


# ---------------- USER DASHBOARD ----------------


@login_required
def user_dashboard(request):
    user = request.user

    # Messages: show only rooms the user participates in
    rooms = ChatRoom.objects.filter(participants=user).prefetch_related("messages", "listing")
    messages_by_room = []
    total_unread_messages = 0
    for room in rooms:
        latest_messages = room.messages.order_by("-timestamp")[:5]  # last 5 per room
        # Count only true unread messages
        unread_count = room.messages.filter(status__in=["sent", "delivered"]) \
                                    .exclude(read_by=user) \
                                    .exclude(sender=user) \
                                    .count()
        total_unread_messages += unread_count
        messages_by_room.append({
            "room": room,
            "listing": room.listing,
            "messages": latest_messages,
            "unread_count": unread_count,
        })

    # Bookings: both customer and provider
    my_bookings = Booking.objects.filter(
        Q(customer=user) | Q(listing__user=user)
    ).order_by("-created_at")

    # Add unread message count per booking
    for booking in my_bookings:
        booking.unread_messages_count = Message.objects.filter(
            room__listing=booking.listing,
            status__in=["sent", "delivered"]
        ).exclude(read_by=user).exclude(sender=user).count()

    # Reviews: received (provider) or given (buyer)
    reviews_qs = None
    if hasattr(user, "reviews_received"):
        reviews_qs = user.reviews_received.all()
    elif hasattr(user, "reviews_given"):
        reviews_qs = user.reviews_given.all()

    # Notifications
    notifications = Notification.objects.filter(user=user).order_by("-timestamp")
    notifications_unread_count = notifications.filter(is_read=False).count()

    context = {
        "user": user,
        "notifications": notifications,
        "notifications_unread_count": notifications_unread_count,
        "wallet": getattr(user, "wallet", None),
        "my_listings": user.listings.all() if user.role == "provider" else None,
        "my_bookings": my_bookings,
        "listing_views": sum(l.views for l in user.listings.all()) if user.role == "provider" else 0,
        "completed_jobs": Booking.objects.filter(listing__user=user, status="approved").count() if user.role == "provider" else 0,
        "avg_rating": round(
            sum(r.rating for r in user.reviews_received.all()) / user.reviews_received.count(), 1
        ) if user.role == "provider" and user.reviews_received.exists() else None,
        "messages_by_room": messages_by_room,
        "messages_unread_count": total_unread_messages,
        "reviews": reviews_qs,
    }

    return render(request, "dashboard/user_dashboard.html", context)

# ---------------- ADMIN DASHBOARD ----------------
from django.db.models import Sum
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from accounts.models import CustomUser, AuditLog
from listings.models import Listing, Booking
from accounts.models import Transaction  # 👈 make sure you import this

@staff_member_required
def admin_dashboard(request):
    context = {
        "all_users": CustomUser.objects.all().order_by("-created_at"),
        "all_listings": Listing.objects.exclude(status="deleted").order_by("-created_at"),
        "all_bookings": Booking.objects.exclude(status="cancelled").order_by("-created_at"),
        "audit_logs": AuditLog.objects.all().order_by("-timestamp"),

        # ✅ new summary metrics
        "total_users": CustomUser.objects.count(),
        "total_listings": Listing.objects.exclude(status="deleted").count(),
        "total_market": Transaction.objects.aggregate(Sum("amount"))["amount__sum"] or 0,
        "total_service_fees": Transaction.objects.aggregate(Sum("service_fee"))["service_fee__sum"] or 0,
    }
    return render(request, "dashboard/admin_dashboard.html", context)


@staff_member_required
def admin_dashboard_stats(request):
    stats = {
      "total_users": CustomUser.objects.count(),
        "verified_users": CustomUser.objects.filter(is_verified=True).count(),
        "total_listings": Listing.objects.exclude(status="deleted").count(),
        "approved_listings": Listing.objects.filter(status="approved").count(),
        "total_bookings": Booking.objects.exclude(status="cancelled").count(),
        "completed_bookings": Booking.objects.filter(status="approved").count(),
        "paid_providers": CustomUser.objects.filter(role="provider", is_paid=True).count(),
        "unpaid_providers": CustomUser.objects.filter(role="provider", is_paid=False).count(),
    }
    return JsonResponse(stats)


# ---------------- HTMX PARTIALS ----------------
@staff_member_required
def admin_users_partial(request):
    users = CustomUser.objects.all().order_by("-created_at")
    return render(request, "dashboard/partials/users_table.html", {"all_users": users})

@staff_member_required
def admin_logs_partial(request):
    logs = AuditLog.objects.all().order_by("-timestamp")[:20]  # latest 20
    return render(request, "dashboard/partials/logs_table.html", {"audit_logs": logs})


from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from listings.models import Listing

@staff_member_required
def admin_listings_partial(request):
    # Pull all listings, newest first
    listings = Listing.objects.all().order_by("-created_at")

    return render(
        request,
        "dashboard/partials/listings_table.html",
        {"all_listings": listings}
    )

@staff_member_required
def admin_bookings_partial(request):
    bookings = Booking.objects.exclude(status="cancelled").order_by("-created_at")
    return render(request, "dashboard/partials/bookings_table.html", {"all_bookings": bookings})


# ---------------- VERIFICATION MODAL + ACTIONS ----------------
@staff_member_required
def admin_user_verification_partial(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    return render(request, "dashboard/partials/verification_modal.html", {"user": user})

@staff_member_required
def admin_manage_user(request, user_id, action):
    user = get_object_or_404(CustomUser, id=user_id)

    if action == "approve":
        user.verification_status = "approved"
        user.is_verified = True
        user.verified_by = request.user
        user.save()
        AuditLog.objects.create(actor=request.user, action="Approved user", target_user=user)

    elif action == "suspend":
        user.verification_status = "rejected"
        user.is_verified = False
        user.verified_by = request.user
        user.save()
        AuditLog.objects.create(actor=request.user, action="Suspended user", target_user=user)

    elif action == "delete":
        AuditLog.objects.create(actor=request.user, action="Deleted user", target_user=user)
        user.delete()

    else:
        return JsonResponse({"error": "Invalid action"}, status=400)

    users = CustomUser.objects.all().order_by("-created_at")
    return render(request, "dashboard/partials/users_table.html", {"all_users": users})


# ---------------- LISTINGS ACTIONS ----------------
@staff_member_required
def admin_manage_listing(request, listing_id, action):
    listing = get_object_or_404(Listing, id=listing_id)

    if action == "approve":
        listing.status = "approved"
        listing.save()
        AuditLog.objects.create(actor=request.user, action="Approved listing", target_user=listing.user)

    elif action == "suspend":
        listing.status = "suspended"
        listing.save()
        AuditLog.objects.create(actor=request.user, action="Suspended listing", target_user=listing.user)

    elif action == "delete":
        listing.status = "deleted"
        listing.is_active = False
        listing.save()
        AuditLog.objects.create(actor=request.user, action="Deleted listing", target_user=listing.user)

    else:
        return JsonResponse({"error": "Invalid action"}, status=400)

    listings = Listing.objects.exclude(status="deleted").order_by("-created_at")
    return render(request, "dashboard/partials/listings_table.html", {"all_listings": listings})


# ---------------- BOOKINGS ACTIONS ----------------
@staff_member_required
def admin_manage_booking(request, booking_id, action):
    booking = get_object_or_404(Booking, id=booking_id)

    if action == "approve":
        booking.status = "approved"
        booking.save()
        AuditLog.objects.create(actor=request.user, action="Approved booking", target_user=booking.customer)

    elif action == "accept":
        booking.status = "accepted"
        booking.save()
        AuditLog.objects.create(actor=request.user, action="Accepted booking", target_user=booking.customer)

    elif action == "reject":
        booking.status = "rejected"
        booking.save()
        AuditLog.objects.create(actor=request.user, action="Rejected booking", target_user=booking.customer)

    elif action == "cancel":
        booking.status = "cancelled"
        booking.save()
        AuditLog.objects.create(actor=request.user, action="Cancelled booking", target_user=booking.customer)

    else:
        return JsonResponse({"error": "Invalid action"}, status=400)

    bookings = Booking.objects.exclude(status="cancelled").order_by("-created_at")
    return render(request, "dashboard/partials/bookings_table.html", {"all_bookings": bookings})

from django.contrib import messages

@login_required
def provider_bookings(request):
    if not request.user.is_paid:
        messages.error(request, "You must complete payment before accessing bookings.")
        return redirect("accounts:payment_gateway")
    bookings = Booking.objects.filter(provider=request.user).order_by("-created_at")
    return render(request, "listings/provider_bookings.html", {"bookings": bookings})

@login_required
def notifications_partial(request):
    notifications_qs = request.user.message_notifications.order_by("-timestamp")
    notifications = notifications_qs[:10]  # slice AFTER
    unread_count = notifications_qs.filter(is_read=False).count()

    return render(request, "dashboard/partials/notifications_panel.html", {
        "notifications": notifications,
        "notifications_unread_count": unread_count,
    })
    
@login_required
def wallet_partial(request):
    # Assuming you have a Wallet model linked to the user
    wallet = getattr(request.user, "wallet", None)
    return render(request, "dashboard/partials/wallet_panel.html", {"wallet": wallet})

from listings.models import Review

@login_required
def buyer_stats_partial(request):
    # Upcoming bookings (buyer side)
    upcoming_bookings_count = request.user.bookings.filter(status="approved").count()

    # Unread messages (using ChatRoom + Message model)
    unread_total = 0
    for room in request.user.rooms.all():
        unread_total += room.unread_count_for(request.user)

    # Reviews given (reviews written by this user)
    buyer_reviews_count = request.user.reviews.count()

    # Feedback received (reviews left on this user's listings)
    buyer_feedback_count = Review.objects.filter(listing__user=request.user).count()

    # Updates / notifications (using Notification model with related_name="message_notifications")
    buyer_updates_count = request.user.message_notifications.filter(is_read=False).count()

    return render(request, "dashboard/partials/buyer_stats_panel.html", {
        "upcoming_bookings_count": upcoming_bookings_count,
        "messages_unread_count": unread_total,
        "buyer_reviews_count": buyer_reviews_count,
        "buyer_feedback_count": buyer_feedback_count,
        "buyer_updates_count": buyer_updates_count,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from accounts .models import Transaction

@login_required
def provider_stats_partial(request):
    # Listings stats
    listings_count = request.user.listings.count()
    pending_listings_count = request.user.listings.filter(status="pending").count()
    suspended_listings_count = request.user.listings.filter(status__in=["suspended", "deleted"]).count()

    # Bookings stats (provider side)
    provider_bookings_count = request.user.provider_bookings.count()

    # Reviews stats (reviews left for this provider’s listings)
    provider_reviews_count = request.user.reviews.count()

    # Updates / notifications (using your Notification model with related_name="message_notifications")
    provider_updates_count = request.user.message_notifications.filter(is_read=False).count()

    return render(request, "dashboard/partials/provider_stats_panel.html", {
        "listings_count": listings_count,
        "pending_listings_count": pending_listings_count,
        "suspended_listings_count": suspended_listings_count,
        "provider_bookings_count": provider_bookings_count,
        "provider_reviews_count": provider_reviews_count,
        "provider_updates_count": provider_updates_count,
    })

@login_required
def messages_partial(request):
    rooms = request.user.chat_rooms.all().prefetch_related("messages", "listing")
    messages_by_room = []
    unread_total = 0

    for room in rooms:
        unread_count = room.messages.exclude(read_by=request.user).count()
        unread_total += unread_count
        messages_by_room.append({
            "room": room,
            "listing": getattr(room, "listing", None),
            "messages": room.messages.order_by("-timestamp")[:5],
            "unread_count": unread_count,
        })

    return render(request, "dashboard/partials/messages_panel.html", {
        "messages_by_room": messages_by_room,
        "messages_unread_count": unread_total,
        "user": request.user,
    })

@login_required
def all_bookings(request):
    # Query all bookings for this user
    bookings = request.user.bookings.all().order_by("-date")
    return render(request, "dashboard/all_bookings.html", {"bookings": bookings})

@login_required
def provider_reviews(request):
    reviews = request.user.reviews.all().order_by("-created_at")
    return render(request, "dashboard/provider_reviews.html", {"reviews": reviews})


@login_required
def dashboard_chats(request):
    rooms = request.user.rooms.prefetch_related("messages", "listing")
    # Attach unread counts for each room
    for room in rooms:
        room.unread_count = room.unread_count_for(request.user)
    return render(request, "dashboard/partials/dashboard_chats.html", {"rooms": rooms})

@login_required
def admin_transactions_partial(request):
    transactions = Transaction.objects.order_by("-timestamp")[:20]
    return render(request, "dashboard/partials/transactions_table.html", {"transactions": transactions})

from django.http import JsonResponse
from .models import SupportTicket
from listings.models import Booking

def support_tickets_json(request):
    tickets = SupportTicket.objects.filter(user=request.user).order_by('-created_at')
    data = [
        {
            "id": t.id,
            "subject": t.subject,
            "message": t.message,
            "status": t.status,
            "created_at": t.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for t in tickets
    ]
    return JsonResponse({"tickets": data})

def pending_payments_json(request):
    payments = Booking.objects.filter(payment_status="pending").order_by('-created_at')
    data = [
        {
            "id": p.id,
            "listing": p.listing.product_name,
            "customer": p.customer.username,
            "provider": p.provider.username,
            "status": p.payment_status,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for p in payments
    ]
    return JsonResponse({"payments": data})
