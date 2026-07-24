from django.db import models
from django.conf import settings

class MarketplaceSettings(models.Model):
    service_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Service Fee: {self.service_fee_percentage}%"


class Dispute(models.Model):
    STATUS_CHOICES = [('open', 'Open'), ('closed', 'Closed'), ('resolved', 'Resolved')]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="disputes_as_customer", on_delete=models.CASCADE, null=True, blank=True)
    provider = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="disputes_as_provider", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Dispute {self.id} - {self.status}"


class SupportTicket(models.Model):
    STATUS_CHOICES = [('open','Open'),('resolved','Resolved'),('escalated','Escalated')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} by {self.user.username} - {self.status}"
