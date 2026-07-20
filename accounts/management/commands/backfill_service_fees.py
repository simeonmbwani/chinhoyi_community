from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import Transaction

class Command(BaseCommand):
    help = "Backfill missing service fees for old transactions"

    def handle(self, *args, **options):
        updated_count = 0

        for tx in Transaction.objects.filter(service_fee=0):
            if tx.listing and tx.listing.price:
                # Example: flat fee of 2.50
                tx.service_fee = Decimal("2.50")
                tx.amount = tx.listing.price + tx.service_fee
            else:
                # Transactions without a listing (provider activation, etc.)
                tx.service_fee = Decimal("2.50")
                tx.amount = tx.service_fee

            tx.save()
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Backfilled service fees for {updated_count} transactions."
        ))
