from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Message
from notifications.models import Notification

@receiver(post_save, sender=Message)
def create_message_notification(sender, instance, created, **kwargs):
    if created:
        # Notify all participants except the sender
        for participant in instance.room.participants.exclude(id=instance.sender.id):
            Notification.objects.create(
                user=participant,
                message=f"New message from {instance.sender.username}: {instance.content[:50]}"
            )
