import os
import django
import random
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import User, Doctor, Patient, DoctorSpecialization
from django.db import transaction

# Doctor specializations
specializations_data = [
    {'name': 'Cardiology', 'description': 'Diagnosis and treatment of heart diseases'},
    {'name': 'Dermatology', 'description': 'Diagnosis and treatment of skin disorders'},
    {'name': 'Neurology', 'description': 'Diagnosis and treatment of nervous system disorders'},
    {'name': 'Orthopedics', 'description': 'Diagnosis and treatment of musculoskeletal disorders'},
    {'name': 'Pediatrics', 'description': 'Medical care of infants, children, and adolescents'},
    {'name': 'Psychiatry', 'description': 'Diagnosis and treatment of mental disorders'},
    {'name': 'Ophthalmology', 'description': 'Diagnosis and treatment of eye disorders'},
    {'name': 'Gynecology', 'description': 'Medical practice dealing with women\'s health'},
    {'name': 'Endocrinology', 'description': 'Diagnosis and treatment of hormone-related diseases'},
    {'name': 'Gastroenterology', 'description': 'Diagnosis and treatment of digestive system disorders'}
]

# Create specializations
specializations = []
for spec_data in specializations_data:
    spec, created = DoctorSpecialization.objects.get_or_create(
        name=spec_data['name'],
        defaults={'description': spec_data['description']}
    )
    specializations.append(spec)
    status = "Created" if created else "Already exists"
    print(f"{status}: {spec.name}")

# Admin data
admin_data = [
    {'email': 'admin1@emedic.com', 'first_name': 'Admin1', 'last_name': 'User'},
    {'email': 'admin2@emedic.com', 'first_name': 'Admin2', 'last_name': 'User'},
    {'email': 'admin3@emedic.com', 'first_name': 'Admin3', 'last_name': 'User'},
    {'email': 'admin4@emedic.com', 'first_name': 'Admin4', 'last_name': 'User'},
    {'email': 'admin5@emedic.com', 'first_name': 'Admin5', 'last_name': 'User'},
    {'email': 'admin6@emedic.com', 'first_name': 'Admin6', 'last_name': 'User'},
    {'email': 'admin7@emedic.com', 'first_name': 'Admin7', 'last_name': 'User'},
    {'email': 'admin8@emedic.com', 'first_name': 'Admin8', 'last_name': 'User'},
    {'email': 'admin9@emedic.com', 'first_name': 'Admin9', 'last_name': 'User'},
]

# Doctor data
doctor_data = [
    {'email': 'doctor1@emedic.com', 'first_name': 'John', 'last_name': 'Smith'},
    {'email': 'doctor2@emedic.com', 'first_name': 'Emily', 'last_name': 'Johnson'},
    {'email': 'doctor3@emedic.com', 'first_name': 'Michael', 'last_name': 'Davis'},
    {'email': 'doctor4@emedic.com', 'first_name': 'Sarah', 'last_name': 'Wilson'},
    {'email': 'doctor5@emedic.com', 'first_name': 'David', 'last_name': 'Martinez'},
    {'email': 'doctor6@emedic.com', 'first_name': 'Jessica', 'last_name': 'Taylor'},
    {'email': 'doctor7@emedic.com', 'first_name': 'Robert', 'last_name': 'Anderson'},
    {'email': 'doctor8@emedic.com', 'first_name': 'Jennifer', 'last_name': 'Thomas'},
    {'email': 'doctor9@emedic.com', 'first_name': 'William', 'last_name': 'Jackson'},
]

# Patient data
patient_data = [
    {'email': 'patient1@example.com', 'first_name': 'Alice', 'last_name': 'Brown'},
    {'email': 'patient2@example.com', 'first_name': 'Bob', 'last_name': 'Miller'},
    {'email': 'patient3@example.com', 'first_name': 'Carol', 'last_name': 'Garcia'},
    {'email': 'patient4@example.com', 'first_name': 'Daniel', 'last_name': 'Rodriguez'},
    {'email': 'patient5@example.com', 'first_name': 'Emma', 'last_name': 'Martinez'},
    {'email': 'patient6@example.com', 'first_name': 'Frank', 'last_name': 'Hernandez'},
    {'email': 'patient7@example.com', 'first_name': 'Grace', 'last_name': 'Lopez'},
    {'email': 'patient8@example.com', 'first_name': 'Henry', 'last_name': 'Gonzalez'},
    {'email': 'patient9@example.com', 'first_name': 'Isabella', 'last_name': 'Wilson'},
]

# Create admin users
print("\nCreating admin users...")
for admin in admin_data:
    try:
        with transaction.atomic():
            # Skip if user already exists
            if User.objects.filter(email=admin['email']).exists():
                print(f"Admin already exists: {admin['email']}")
                continue
                
            user = User.objects.create_user(
                email=admin['email'],
                password='Admin123!',
                first_name=admin['first_name'],
                last_name=admin['last_name'],
                role='ADMIN',
                is_staff=True,
                is_superuser=True,
                phone_number=f'+1555{random.randint(1000000, 9999999)}'
            )
            print(f"Created admin: {user.email} (Password: Admin123!)")
    except Exception as e:
        print(f"Error creating admin {admin['email']}: {str(e)}")

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
            spec_count = random.randint(1, 3)
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

# Print all credentials
print("\n" + "="*50)
print("USER CREDENTIALS")
print("="*50)

print("\nADMIN USERS:")
print("Main admin: admin@emedic.com / Admin123!")
for admin in admin_data:
    print(f"  {admin['email']} / Admin123!")

print("\nDOCTOR USERS:")
print("Main doctor: doctor@emedic.com / Doctor123!")
for doctor in doctor_data:
    print(f"  {doctor['email']} / Doctor123!")

print("\nPATIENT USERS:")
print("Main patient: patient@example.com / Patient123!")
for patient in patient_data:
    print(f"  {patient['email']} / Patient123!")

print("\n" + "="*50)
print("YOU CAN NOW LOG IN WITH ANY OF THESE CREDENTIALS")
print("="*50)