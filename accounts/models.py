from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from listings.models import Listing
from .validators import validate_id_document

class CustomUser(AbstractUser):
    ROLE_CHOICES = (('buyer', 'Buyer'), ('provider', 'Provider'))
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')

    is_provider = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    id_document = models.FileField(upload_to='verifications/', null=True, blank=True,
                                   validators=[validate_id_document])
    STATUS_CHOICES = (('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'))
    verification_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True,
                                    related_name="verifications_done", on_delete=models.SET_NULL)
    rejection_reason = models.TextField(blank=True, null=True)

    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    business_name = models.CharField(max_length=100, blank=True)

    LANGUAGE_CHOICES = [('en', 'English'), ('sn', 'Shona'), ('nd', 'Ndebele')]
    language_preference = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')
    theme_preference = models.CharField(max_length=10, default='light')

    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    groups = models.ManyToManyField(Group, blank=True, related_name="customuser_set")
    user_permissions = models.ManyToManyField(Permission, blank=True, related_name="customuser_set")

    def __str__(self):
        return f"{self.username} ({self.role})"


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s Wallet"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


class Transaction(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("success", "Success"), ("failed", "Failed")]
    TRANSACTION_TYPES = [("deposit", "Deposit"), ("withdrawal", "Withdrawal"), ("payment", "Payment")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True, related_name="transactions")
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, blank=True, null=True, related_name="transactions")

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default="payment")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reference = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} of ${self.amount} by {self.user.username} ({self.status})"


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="audit_actions")
    action = models.CharField(max_length=255)
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="audit_targets")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.actor} {self.action} → {self.target_user} ({self.timestamp})"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
