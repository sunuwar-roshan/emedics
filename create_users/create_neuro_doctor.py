import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Doctor, DoctorSpecialization
from django.db import transaction

# Create a neurologist
with transaction.atomic():
    try:
        # Create doctor user
        if not User.objects.filter(email='doctor3@emedic.com').exists():
            doctor_user = User.objects.create_user(
                email='doctor3@emedic.com', 
                password='Doctor123!', 
                first_name='Michael', 
                last_name='Davis', 
                role='DOCTOR', 
                phone_number='+15551112222'
            )
            
            # Find specialization
            spec = DoctorSpecialization.objects.get(name='Neurology')
            
            # Create doctor profile
            doctor_profile = Doctor.objects.create(
                user=doctor_user, 
                license_number='MD789012', 
                qualification='MD', 
                experience_years=15, 
                consultation_fee=3000, 
                bio='Dr. Davis is a neurologist with extensive experience in treating neurological disorders.'
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