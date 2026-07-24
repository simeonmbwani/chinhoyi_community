from django import forms
from .models import CustomUser

class UserRegistrationForm(forms.ModelForm):
    # Checkbox for Terms and Conditions
    terms_accepted = forms.BooleanField(
        required=True,
        label="I agree to the Terms and Conditions",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 
        'placeholder': 'Create a secure password'
    }))
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number', 'role', 
            'business_name', 'language_preference', 'id_document', 'terms_accepted'
        ]
        
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter your unique username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'username@gmail.com'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '+263...'
            }),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'business_name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Your business or shop name'
            }),
            'language_preference': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('en', 'English'), ('sn', 'Shona')]
            ),
            'id_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
        labels = {
            'id_document': 'Upload ID or Proof of Ownership',
            'business_name': 'Business/Organization Name (Optional)',
        }
        
        help_texts = {
            'id_document': 'Accepted: PDF, JPG, PNG. Mandatory for verification.',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'phone_number', 'business_name', 
            'bio', 'profile_picture', 'language_preference', 'theme_preference'
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'language_preference': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('en', 'English'), ('sn', 'Shona')]
            ),
            'theme_preference': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('light', 'Light'), ('dark', 'Dark')]
            ),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'bio', 'phone_number', 'business_name', 'id_document']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'id_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
