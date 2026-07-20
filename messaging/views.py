from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from listings.models import Listing
from messaging.models import ChatRoom, Message

User = get_user_model()

# Inbox: list all chat rooms for the logged-in user
@login_required
def inbox_view(request):
    user = request.user
    rooms = ChatRoom.objects.filter(participants=user).prefetch_related("messages", "listing")

    inbox_data = []
    for room in rooms:
        last_msg = room.messages.order_by("-timestamp").first()
        unread_count = room.unread_count_for(user)
        inbox_data.append({
            "room": room,
            "listing": room.listing,
            "last_message": last_msg,
            "unread_count": unread_count,
        })

    return render(request, "messaging/inbox.html", {
        "inbox_data": inbox_data,
    })

# chat/views.py
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.all().order_by("timestamp")

    # Mark messages as delivered if recipient is viewing
    for msg in messages.exclude(sender=request.user).filter(status="sent"):
        msg.mark_delivered()

    # Mark messages as read once displayed
    for msg in messages.exclude(sender=request.user).filter(status="delivered"):
        msg.read_by.add(request.user)
        msg.mark_read()

    unread_count = room.unread_count_for(request.user)

    return render(request, "messaging/chat_room.html", {
        "room": room,
        "messages": messages,
        "user": request.user,
        "unread_count": unread_count,
    })

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user)
    messages = room.messages.all()

    # Mark as delivered: any "sent" messages not from this user
    for msg in messages.exclude(sender=request.user).filter(status="sent"):
        msg.mark_delivered()

    # Mark as read: any "delivered" messages not from this user
    for msg in messages.exclude(sender=request.user).filter(status="delivered"):
        msg.mark_read(request.user)   # now handles both status + read_by

    # Unread count for badge display
    unread_count = room.unread_count_for(request.user)

    return render(request, "messaging/chat_room.html", {
        "room": room,
        "messages": messages.order_by("timestamp"),
        "user": request.user,
        "unread_count": unread_count,
    })


# Start chat from a listing
@login_required
def start_chat_from_listing(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    provider = listing.user

    if request.user == provider:
        return redirect("listings:listing_detail", pk=listing.id)

    room = ChatRoom.objects.filter(listing=listing, participants=request.user).first()
    if not room:
        room = ChatRoom.objects.create(listing=listing)
        room.participants.add(request.user, provider)

    return redirect("messaging:chat_room", room_id=room.id)

# Send a message via AJAX (supports text + file attachments)
# chat/views.py
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message

@login_required
def send_message(request, room_id):
    if request.method == "POST":
        room = get_object_or_404(ChatRoom, id=room_id)
        content = request.POST.get("message", "").strip()
        file = request.FILES.get("file")

        if not content and not file:
            return JsonResponse({"success": False, "error": "Empty message."})

        msg = Message.objects.create(
            room=room,
            sender=request.user,
            content=content if content else None,
            file=file if file else None,
            file_type="file" if file else "text",
            status="sent"
        )

        # ✅ Ensure both participants see it
        for participant in room.participants.exclude(id=request.user.id):
            msg.mark_delivered()

        return JsonResponse({
            "success": True,
            "id": msg.id,
            "content": msg.content or "",
            "file_url": msg.file.url if msg.file else None,
            "timestamp": msg.timestamp.strftime("%H:%M"),
            "status": msg.status
        })

# Fetch messages via AJAX
@login_required
def fetch_messages(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    messages = room.messages.order_by("timestamp")
    data = [
        {
            "sender": m.sender.username,
            "content": m.content or "",
            "file_url": m.file.url if m.file else "",
            "file_type": m.file_type,
            "status": m.status,
            "timestamp": m.timestamp.strftime("%H:%M"),
        }
        for m in messages
    ]
    return JsonResponse({"messages": data})

# Message provider directly by provider_id
@login_required
def message_provider(request, provider_id):
    provider = get_object_or_404(User, id=provider_id)

    if request.user == provider:
        return redirect("messaging:inbox")

    room = ChatRoom.objects.filter(participants=request.user).filter(participants=provider).first()
    if not room:
        room = ChatRoom.objects.create()
        room.participants.add(request.user, provider)

    return redirect("messaging:chat_room", room_id=room.id)

# messaging/views.py
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model


User = get_user_model()

@login_required
def chat_view(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)

    # Prevent chatting with yourself
    if recipient == request.user:
        return redirect("messaging:inbox")

    # Find existing room or create new one
    room = ChatRoom.objects.filter(participants=request.user).filter(participants=recipient).first()
    if not room:
        room = ChatRoom.objects.create()
        room.participants.add(request.user, recipient)

    # Redirect to the chat_room view
    return redirect("messaging:chat_room", room_id=room.id)


@login_required
def bulk_action_chats(request):
    if request.method == "POST":
        room_ids = request.POST.getlist("rooms_selected")
        action = request.POST.get("action")

        for rid in room_ids:
            room = get_object_or_404(ChatRoom, id=rid, participants=request.user)
            if action == "delete":
                room.messages.all().delete()  # hard delete
            elif action == "archive":
                room.is_archived = True
                room.save()

        return redirect("messaging:inbox")
    return redirect("messaging:inbox")

@login_required
def unread_count_api(request):
    total_unread = sum(
        room.unread_count_for(request.user)
        for room in ChatRoom.objects.filter(participants=request.user)
    )
    return JsonResponse({"unread_count": total_unread})

@login_required
def provider_chats(request):
    rooms = request.user.chat_rooms.all().prefetch_related("messages")
    return render(request, "messaging/provider_chats.html", {"rooms": rooms})
