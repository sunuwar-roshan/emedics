import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Doctor, DoctorSpecialization
from django.db import transaction

# Create more doctors with different specializations
doctors_data = [
    {
        'email': 'doctor3@emedic.com',
        'first_name': 'Michael',
        'last_name': 'Davis',
        'specialization': 'Neurology',
        'license': 'MD789012',
        'experience': 15,
        'fee': 3000,
        'bio': 'Dr. Davis is a neurologist with extensive experience in treating neurological disorders.'
    },
    {
        'email': 'doctor4@emedic.com',
        'first_name': 'Sarah',
        'last_name': 'Wilson',
        'specialization': 'Pediatrics',
        'license': 'MD345678',
        'experience': 12,
        'fee': 2200,
        'bio': 'Dr. Wilson is a pediatrician who specializes in child healthcare from infancy through adolescence.'
    },
    {
        'email': 'doctor5@emedic.com',
        'first_name': 'David',
        'last_name': 'Martinez',
        'specialization': 'Orthopedics',
        'license': 'MD234567',
        'experience': 18,
        'fee': 3500,
        'bio': 'Dr. Martinez is an orthopedic surgeon specializing in joint replacements and sports injuries.'
    }
]

for doctor_data in doctors_data:
    try:
        with transaction.atomic():
            # Check if user already exists
            if User.objects.filter(email=doctor_data['email']).exists():
                print(f"Doctor already exists: {doctor_data['email']}")
                continue
                
            # Create doctor user
            doctor_user = User.objects.create_user(
                email=doctor_data['email'],
                password='Doctor123!',
                first_name=doctor_data['first_name'],
                last_name=doctor_data['last_name'],
                role='DOCTOR',
                phone_number='+1555' + ''.join([str(i) for i in range(7)])
            )
            
            # Create doctor profile
            doctor_profile = Doctor.objects.create(
                user=doctor_user,
                license_number=doctor_data['license'],
                qualification='MD',
                experience_years=doctor_data['experience'],
                consultation_fee=doctor_data['fee'],
                bio=doctor_data['bio']
            )
            
            # Add specialization
            spec = DoctorSpecialization.objects.get(name=doctor_data['specialization'])
            doctor_profile.specializations.add(spec)
            
            print(f"Created doctor: {doctor_user.email} (Password: Doctor123!)")
    except Exception as e:
        print(f"Error creating doctor {doctor_data['email']}: {str(e)}")

# Print updated count
print("\nUser counts:")
print(f"Admin users: {User.objects.filter(role='ADMIN').count()}")
print(f"Doctor users: {User.objects.filter(role='DOCTOR').count()}")
print(f"Patient users: {User.objects.filter(role='PATIENT').count()}")