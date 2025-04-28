import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Patient
from django.db import transaction

# Create another patient
with transaction.atomic():
    try:
        # Create patient user
        if not User.objects.filter(email='patient3@example.com').exists():
            patient_user = User.objects.create_user(
                email='patient3@example.com', 
                password='Patient123!', 
                first_name='Carol', 
                last_name='Garcia', 
                role='PATIENT', 
                phone_number='+15553334444'
            )
            
            # Create patient profile
            Patient.objects.create(
                user=patient_user, 
                date_of_birth='1982-03-25', 
                gender='F', 
                address='789 Pine St, Somewhere, USA', 
                blood_group='A-', 
                emergency_contact_name='Joe Garcia', 
                emergency_contact_number='+15556667777'
            )
            print('Patient created successfully')
        else:
            print('Patient already exists')
    except Exception as e:
        print(f'Error creating patient: {str(e)}')

# Print count
admin_count = User.objects.filter(role='ADMIN').count()
doctor_count = User.objects.filter(role='DOCTOR').count()
patient_count = User.objects.filter(role='PATIENT').count()
print(f'Admin users: {admin_count}, Doctor users: {doctor_count}, Patient users: {patient_count}')