from django.core.exceptions import ValidationError

def validate_id_document(value):
    # Only allow images (ID photos)
    if not value.name.endswith(('.jpg', '.jpeg', '.png')):
        raise ValidationError("Only JPG or PNG images of your ID or Proof of Ownership are accepted.")
    # Limit size to 5MB
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("File too large! Please upload an image smaller than 5MB.")