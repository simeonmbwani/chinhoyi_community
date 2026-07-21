from django import forms
from .models import Listing, Feedback              # Feedback is in listings.models
from dashboard.models import SupportTicket         # SupportTicket is in dashboard.models
Feedback   # 👈 fixed import

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['product_name', 'description', 'category', 'price', 'location', 'image']
        labels = {
            'product_name': 'Listing Title',
            'price': 'Price (USD)',
            'location': 'Suburb/Location',
        }
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 2-Bedroom Cottage in Mzari'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe the property or service in detail...'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Chinhoyi'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class SupportTicketForm(forms.ModelForm):
    class Meta:
        model = SupportTicket
        fields = ["subject", "message", "status"]   # matches dashboard.SupportTicket


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["message"]
