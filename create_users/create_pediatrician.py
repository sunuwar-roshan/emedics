import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Doctor, DoctorSpecialization
from django.db import transaction

# Create a pediatrician
with transaction.atomic():
    try:
        # Create doctor user
        if not User.objects.filter(email='doctor4@emedic.com').exists():
            doctor_user = User.objects.create_user(
                email='doctor4@emedic.com', 
                password='Doctor123!', 
                first_name='Sarah', 
                last_name='Wilson', 
                role='DOCTOR', 
                phone_number='+15558889999'
            )
            
            # Find specialization
            spec = DoctorSpecialization.objects.get(name='Pediatrics')
            
            # Create doctor profile
            doctor_profile = Doctor.objects.create(
                user=doctor_user, 
                license_number='MD345678', 
                qualification='MD, PhD', 
                experience_years=12, 
                consultation_fee=2200, 
                bio='Dr. Wilson is a pediatrician who specializes in child healthcare from infancy through adolescence.'
            )
            doctor_profile.specializations.add(spec)
            print('Doctor created successfully')
        else:
            print('Doctor already exists')
    except Exception as e:
        print(f'Error creating doctor: {str(e)}')

# Print count
admin_count = User.objects.filter(role='ADMIN').count()
doctor_count = User.objects.filter(role='DOCTOR').count()
patient_count = User.objects.filter(role='PATIENT').count()
print(f'Admin users: {admin_count}, Doctor users: {doctor_count}, Patient users: {patient_count}')