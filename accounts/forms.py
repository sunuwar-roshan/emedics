from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    phone = forms.CharField(required=True)
    street_address = forms.CharField(required=False, widget=forms.Textarea)
    city = forms.CharField(required=False)
    photo = forms.ImageField(required=False)  # Image field for profile picture
    user_type = forms.ChoiceField(choices=CustomUser.USER_TYPE_CHOICES, required=True)

    # Doctor-specific fields
    specialization = forms.CharField(required=False)
    license_number = forms.CharField(required=False)

    # Patient-specific fields
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=False)
    emergency_contact_number = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'street_address', 'city', 'photo', 
                  'user_type', 'specialization', 'license_number', 'date_of_birth', 
                  'gender', 'emergency_contact_number', 'password1', 'password2']
