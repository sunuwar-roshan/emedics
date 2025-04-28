from django.db import models
from django.utils import timezone

from accounts.models import CustomUser

class Appointment(models.Model):
    """Model for storing appointment information"""
    TIME_SLOTS = [
        ('09:00', '09:00 AM - 09:30 AM'),
        ('09:30', '09:30 AM - 10:00 AM'),
        ('10:00', '10:00 AM - 10:30 AM'),
        ('10:30', '10:30 AM - 11:00 AM'),
        ('11:00', '11:00 AM - 11:30 AM'),
        ('11:30', '11:30 AM - 12:00 PM'),
        ('14:00', '02:00 PM - 02:30 PM'),
        ('14:30', '02:30 PM - 03:00 PM'),
        ('15:00', '03:00 PM - 03:30 PM'),
        ('15:30', '03:30 PM - 04:00 PM'),
        ('16:00', '04:00 PM - 04:30 PM'),
        ('16:30', '04:30 PM - 05:00 PM'),
    ]
    time_slot = models.CharField(max_length=50)
    APPOINTMENT_TYPES = [
        ('consultation', 'General Consultation'),
        ('follow-up', 'Follow-up'),
        ('new-patient', 'New Patient'),
        ('urgent', 'Urgent Care'),
        ('routine-checkup', 'Routine Checkup'),
        ('test-results', 'Test Results Review'),
    ]
    APPOINTMENT_MEDIUMS = [
        ('Physical', 'Physical'),
        ('Online', 'Online'),

    ]

    SPECIALIZATION_CHOICES = [
        ('cardiology', 'Cardiology'),
        ('dermatology', 'Dermatology'),
        ('endocrinology', 'Endocrinology'),
        ('gastroenterology', 'Gastroenterology'),
        ('neurology', 'Neurology'),
        ('orthopedics', 'Orthopedics'),
        ('pediatrics', 'Pediatrics'),
        ('psychiatry', 'Psychiatry'),
        ('pulmonology', 'Pulmonology'),
        ('rheumatology', 'Rheumatology'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rescheduled', 'Rescheduled'),
        ('no-show', 'No Show'),
    ]

    # DOCTORS = CustomUser.objects.filter(user_type = 'doctor').values_list('username', flat=True).distinct()
    # DOCTORS_CHOICES = [(doctor, doctor) for doctor in DOCTORS]
    def get_doctor_choices(self):
        """Dynamically fetch doctor choices at runtime"""
        doctors = CustomUser.objects.filter(user_type='doctor').values_list('username', flat=True).distinct()
        return [(doctor, doctor) for doctor in doctors]
    
    main_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES)
    # doctor_name = models.CharField(max_length=100, choices=DOCTORS_CHOICES)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    patient_name = models.CharField(max_length=100)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=20)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=5, choices=TIME_SLOTS)
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES)
    appointment_mediums = models.CharField(max_length=20, choices=APPOINTMENT_MEDIUMS,default='Physical')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        # Ensure we don't have conflicting appointments
        unique_together = ('doctor_name', 'appointment_date', 'time_slot')
        ordering = ['appointment_date', 'time_slot']

    def str(self):
        return f"Appointment with Dr. {self.doctor_name} on {self.appointment_date} at {self.get_time_slot_display()}"

    def save(self, *args, **kwargs):
        """Ensure doctor_name is valid before saving"""
        if self.doctor_name not in dict(self.get_doctor_choices()):
            raise ValueError("Invalid doctor selected.")
        super().save(*args, **kwargs)
        
    def is_past_due(self):
        """Check if appointment is in the past"""
        return self.appointment_date < timezone.now().date() or \
               (self.appointment_date == timezone.now().date() and 
                self.time_slot < timezone.now().strftime('%H:%M'))
    # Add this to your models.py file
class MedicalRecord(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resolved', 'Resolved'),
        ('follow_up', 'Needs Follow-up'),
        ('referred', 'Referred to Specialist')
    ]
    
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_records')
    patient_name = models.CharField(max_length=100)
    patient_email = models.EmailField()
    diagnosis = models.TextField()
    treatment = models.TextField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Medical record for {self.patient_name} by Dr. {self.doctor.username}"