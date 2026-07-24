from rest_framework.routers import DefaultRouter
from .views import ChatRoomViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='rooms')
router.register(r'messages', MessageViewSet, basename='messages')

urlpatterns = router.urls
