from django.db import models
from django.conf import settings
from django.utils import timezone

class ChatRoom(models.Model):
    listing = models.ForeignKey(
        'listings.Listing',
        on_delete=models.CASCADE,
        related_name='chats',
        null=True,
        blank=True
    )
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def unread_count_for(self, user):
        """
        Count messages that the given user has not read.
        - Only include messages still in 'sent' or 'delivered' state
        - Exclude messages already marked as read by this user
        - Exclude messages sent by this user
        """
        return self.messages.filter(status__in=['sent', 'delivered']) \
                            .exclude(read_by=user) \
                            .exclude(sender=user) \
                            .count()


class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='chat_files/', blank=True, null=True)
    file_type = models.CharField(max_length=20, default='text')
    timestamp = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    delivered_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages', blank=True)

    class Meta:
        ordering = ['timestamp']

    def mark_delivered(self):
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save(update_fields=['status', 'delivered_at'])

    def mark_read(self, user=None):
        """
        Mark this message as read.
        - Update status and timestamp
        - Add user to read_by if provided
        """
        self.status = 'read'
        self.read_at = timezone.now()
        self.save(update_fields=['status', 'read_at'])
        if user:
            self.read_by.add(user)
