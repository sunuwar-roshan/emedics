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
    license_number = forms.CharField(required=False)  # Made optional

    # Patient-specific fields
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    gender = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], required=False)
    emergency_contact_number = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'street_address', 'city', 'photo', 
                  'user_type', 'specialization', 'license_number', 'date_of_birth', 
                  'gender', 'emergency_contact_number', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password validation help texts
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        
        if user_type == 'doctor':
            specialization = cleaned_data.get('specialization')
            if not specialization:
                self.add_error('specialization', 'Specialization is required for doctors')
                
        return cleaned_data

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'photo']
        
    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        
        # Add Bootstrap classes to form fields
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
            
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This email is already in use.')
        return email
