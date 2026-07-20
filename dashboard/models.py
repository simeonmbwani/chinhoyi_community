from django.db import models
from django.db import models
from django.conf import settings

class MarketplaceSettings(models.Model):
    service_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Service Fee: {self.service_fee_percentage}%"

class MarketplaceSettings(models.Model):
    service_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=5.00)

    def __str__(self):
        return "Marketplace Settings"

class Dispute(models.Model):
    # This matches the query used in your view
    status = models.CharField(max_length=20, default='open') # 'open', 'closed', 'resolved'
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"Dispute {self.id} - {self.status}"    

# dashboard/models.py
customer = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    related_name="disputes_as_customer",
    on_delete=models.CASCADE
)
provider = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    related_name="disputes_as_provider",
    on_delete=models.CASCADE
)
# dashboard/models.py
class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="audit_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.actor} {self.action} {self.target_user} at {self.timestamp}"

# dashboard/models.py
class SupportTicket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[('open','Open'),('resolved','Resolved'),('escalated','Escalated')],
        default='open'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} by {self.user.username} - {self.status}"

