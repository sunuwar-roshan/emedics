from django import forms
from django.utils import timezone
from .models import Appointment


class AppointmentForm(forms.ModelForm):
    """Form for creating and editing appointments"""
    
  
    class Meta:
        model = Appointment
        fields = [
            'specialization', 
            'doctor_name', 
            'patient_name', 
            'patient_email', 
            'patient_phone', 
            'appointment_date', 
            'time_slot', 
            'appointment_type', 
            'appointment_mediums',
            'notes'
        ]
        widgets = {
            'specialization': forms.Select(attrs={'class': 'form-select'}),
            'doctor_name': forms.Select(attrs={'class': 'form-select'}),
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'patient_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'patient_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
            'appointment_type': forms.Select(attrs={'class': 'form-select'}),
            'appointment_mediums': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Get the user from kwargs if provided
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If editing an existing appointment, set doctor choices based on specialization
        if self.instance and self.instance.pk and self.instance.specialization:
            doctors = Doctor.objects.filter(specialization=self.instance.specialization).select_related('user')
            doctor_choices = [('', 'Select a doctor')] + [
                (doctor.user.username, f"Dr. {doctor.user.get_full_name() or doctor.user.username}") 
                for doctor in doctors
            ]
            self.fields['doctor_name'].choices = doctor_choices
        
        # If a logged-in user is creating an appointment, pre-fill patient info
        if user and user.is_authenticated and not user.is_doctor:
            self.fields['patient_name'].initial = user.get_full_name() or user.username
            self.fields['patient_email'].initial = user.email
            # Disable patient email to prevent changes
            self.fields['patient_email'].widget.attrs['readonly'] = True
    
    def clean_appointment_date(self):
        """Validate that appointment date is not in the past"""
        date = self.cleaned_data.get('appointment_date')
        if date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date
    
    def clean(self):
        """Cross-field validation"""
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor_name')
        date = cleaned_data.get('appointment_date')
        time_slot = cleaned_data.get('time_slot')
        
        if doctor and date and time_slot:
            # Check if appointment slot is already booked
            conflicts = Appointment.objects.filter(
                doctor_name=doctor,
                appointment_date=date,
                time_slot=time_slot
            )
            
            # If we're editing an existing appointment, exclude it from conflict check
            if self.instance.pk:
                conflicts = conflicts.exclude(pk=self.instance.pk)
                
            if conflicts.exists():
                raise forms.ValidationError(
                    "This appointment slot is already booked. Please select another time."
                )
                
        return cleaned_data