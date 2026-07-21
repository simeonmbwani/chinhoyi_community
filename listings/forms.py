from django import forms
from .models import Listing

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ['product_name', 'description', 'category', 'price', 'location', 'image']

        # Labels for better UX
        labels = {
            'product_name': 'Listing Title',
            'price': 'Price (USD)',
            'location': 'Suburb/Location',
        }

        # Widgets for styling and placeholders
        widgets = {
            'product_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 2-Bedroom Cottage in Mzari'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the property or service in detail...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': '0.00'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Chinhoyi'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
