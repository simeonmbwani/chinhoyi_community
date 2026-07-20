from django import forms
from .models import MarketplaceSettings

class ServiceFeeForm(forms.ModelForm):
    class Meta:
        model = MarketplaceSettings
        fields = ['service_fee_percentage']
        widgets = {
            'service_fee_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
        }