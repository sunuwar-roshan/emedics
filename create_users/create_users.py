import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Doctor, Patient, DoctorSpecialization
from django.db import transaction

# Create a doctor
with transaction.atomic():
    # Create doctor specialization
    cardiology, _ = DoctorSpecialization.objects.get_or_create(
        name='Cardiology',
        defaults={'description': 'Diagnosis and treatment of heart diseases'}
    )
    
    # Create doctor user
    doctor = User.objects.create_user(
        email='doctor@emedic.com',
        password='Doctor123!',
        first_name='John',
        last_name='Smith',
        role='DOCTOR',
        phone_number='+15551234567'
    )
    
    # Create doctor profile
    doctor_profile = Doctor.objects.create(
        user=doctor,
        license_number='MD123456',
        qualification='MD',
        experience_years=10,
        consultation_fee=2500,
        bio='Dr. Smith is a cardiologist with 10 years of experience.'
    )
    
    # Add specialization
    doctor_profile.specializations.add(cardiology)
    
    print(f'Doctor created: {doctor.email} (Password: Doctor123!)')

# Create a patient
with transaction.atomic():
    # Create patient user
    patient = User.objects.create_user(
        email='patient@example.com',
        password='Patient123!',
        first_name='Alice',
        last_name='Johnson',
        role='PATIENT',
        phone_number='+15559876543'
    )
    
    # Create patient profile
    patient_profile = Patient.objects.create(
        user=patient,
        date_of_birth='1990-05-15',
        gender='F',
        address='123 Main St, Anytown, USA',
        blood_group='O+',
        emergency_contact_name='Bob Johnson',
        emergency_contact_number='+15551234567'
    )
    
    print(f'Patient created: {patient.email} (Password: Patient123!)')

print('\nAll users created successfully.')
print('Admin: admin@emedic.com / Admin123!')
print('Doctor: doctor@emedic.com / Doctor123!')
print('Patient: patient@example.com / Patient123!')