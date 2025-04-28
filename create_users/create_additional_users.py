import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Doctor, Patient, DoctorSpecialization
from django.db import transaction

# Get existing specializations
specializations = list(DoctorSpecialization.objects.all())
print(f"Found {len(specializations)} specializations")

# Additional doctor data (smaller set)
doctor_data = [
    {'email': 'doctor2@emedic.com', 'first_name': 'Emily', 'last_name': 'Johnson'},
    {'email': 'doctor3@emedic.com', 'first_name': 'Michael', 'last_name': 'Davis'},
    {'email': 'doctor4@emedic.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
    {'email': 'doctor5@emedic.com', 'first_name': 'David', 'last_name': 'Martinez'},
]

# Additional patient data (smaller set)
patient_data = [
    {'email': 'patient2@example.com', 'first_name': 'Bob', 'last_name': 'Miller'},
    {'email': 'patient3@example.com', 'first_name': 'Carol', 'last_name': 'Garcia'},
    {'email': 'patient4@example.com', 'first_name': 'Daniel', 'last_name': 'Rodriguez'},
    {'email': 'patient5@example.com', 'first_name': 'Emma', 'last_name': 'Martinez'},
]

# Create doctor users
print("\nCreating doctor users...")
for doctor in doctor_data:
    try:
        with transaction.atomic():
            # Skip if user already exists
            if User.objects.filter(email=doctor['email']).exists():
                print(f"Doctor already exists: {doctor['email']}")
                continue
                
            user = User.objects.create_user(
                email=doctor['email'],
                password='Doctor123!',
                first_name=doctor['first_name'],
                last_name=doctor['last_name'],
                role='DOCTOR',
                phone_number=f'+1555{random.randint(1000000, 9999999)}'
            )
            
            # Create doctor profile
            doctor_profile = Doctor.objects.create(
                user=user,
                license_number=f'MD{random.randint(100000, 999999)}',
                qualification=random.choice(['MD', 'MBBS, MD', 'MD, PhD']),
                experience_years=random.randint(2, 25),
                consultation_fee=random.choice([1500, 2000, 2500, 3000, 3500]),
                bio=f'Dr. {user.last_name} is a highly skilled physician with several years of experience.'
            )
            
            # Add 1-3 random specializations
            spec_count = min(random.randint(1, 3), len(specializations))
            selected_specs = random.sample(specializations, spec_count)
            for spec in selected_specs:
                doctor_profile.specializations.add(spec)
            
            print(f"Created doctor: {user.email} (Password: Doctor123!)")
    except Exception as e:
        print(f"Error creating doctor {doctor['email']}: {str(e)}")

# Create patient users
print("\nCreating patient users...")
for patient in patient_data:
    try:
        with transaction.atomic():
            # Skip if user already exists
            if User.objects.filter(email=patient['email']).exists():
                print(f"Patient already exists: {patient['email']}")
                continue
                
            user = User.objects.create_user(
                email=patient['email'],
                password='Patient123!',
                first_name=patient['first_name'],
                last_name=patient['last_name'],
                role='PATIENT',
                phone_number=f'+1555{random.randint(1000000, 9999999)}'
            )
            
            # Generate random date of birth (21-80 years old)
            years = random.randint(21, 80)
            today = datetime.now().date()
            dob = today - timedelta(days=365 * years + random.randint(0, 364))
            
            # Create patient profile
            patient_profile = Patient.objects.create(
                user=user,
                date_of_birth=dob,
                gender=random.choice(['M', 'F', 'O']),
                address=f'{random.randint(1, 9999)} Main Street, City, State, Zip',
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']),
                emergency_contact_name='Emergency Contact',
                emergency_contact_number=f'+1555{random.randint(1000000, 9999999)}'
            )
            
            print(f"Created patient: {user.email} (Password: Patient123!)")
    except Exception as e:
        print(f"Error creating patient {patient['email']}: {str(e)}")

# Print updated count
print("\nUser counts:")
print(f"Admin users: {User.objects.filter(role='ADMIN').count()}")
print(f"Doctor users: {User.objects.filter(role='DOCTOR').count()}")
print(f"Patient users: {User.objects.filter(role='PATIENT').count()}")