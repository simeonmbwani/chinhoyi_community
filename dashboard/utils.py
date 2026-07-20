from messaging.models import ChatRoom

def get_messages_grouped_by_room(user):
    rooms = ChatRoom.objects.filter(participants=user).prefetch_related("messages", "listing")
    groups = []
    for room in rooms:
        messages = room.messages.order_by("-timestamp")[:10]  # latest 10 messages
        unread_count = room.unread_count_for(user)
        groups.append({
            "room": room,
            "listing": getattr(room, "listing", None),
            "messages": messages,
            "unread_count": unread_count,
        })
    return groups
