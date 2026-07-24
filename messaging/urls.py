from django.urls import path, include
from . import views
from .views import start_chat_from_listing
from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet

app_name = "messaging"

# DRF router for API endpoints
router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='rooms')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = [
    # Inbox: list all active conversations
    path("", views.inbox_view, name="inbox"),

    # Chat room by room_id
    path("room/<int:room_id>/", views.chat_room, name="chat_room"),

    # Chat view by recipient_id (create/get room between two users)
    path("chat/<int:recipient_id>/", views.chat_view, name="chat_with_user"),

    # Start chat from a listing
    path("start/<int:listing_id>/", start_chat_from_listing, name="start_chat_from_listing"),

    # AJAX endpoints
    path("chat/<int:room_id>/send/", views.send_message, name="send_message"),
    path("chat/<int:room_id>/fetch/", views.fetch_messages, name="fetch_messages"),

    # Message provider directly by provider_id
    path("message/<int:provider_id>/", views.message_provider, name="message_provider"),
    path("bulk_action/", views.bulk_action_chats, name="bulk_action_chats"),
    path("unread_count/", views.unread_count_api, name="unread_count_api"),
    path("provider/chats/", views.provider_chats, name="provider_chats"),

    # API endpoints (DRF router)
    path("api/", include(router.urls)),
]
