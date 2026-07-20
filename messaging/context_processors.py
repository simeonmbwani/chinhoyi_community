from messaging.models import ChatRoom

def unread_counts(request):
    if request.user.is_authenticated:
        total_unread = sum(
            room.unread_count_for(request.user)
            for room in ChatRoom.objects.filter(participants=request.user)
        )
        return {"global_unread_count": total_unread}
    return {"global_unread_count": 0}
