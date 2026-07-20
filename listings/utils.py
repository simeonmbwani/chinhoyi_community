from decimal import Decimal

def calculate_service_fee(price, category):
    # Convert your percentage to Decimal
    fee_percentage = Decimal('0.05') # Example: 5% fee
    return price * fee_percentage