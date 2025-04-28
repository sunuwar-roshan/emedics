import os
import django
from datetime import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emedic.settings')
django.setup()

from accounts.models import Doctor
from appointments.models import DoctorSchedule, TimeSlot
from django.db import transaction

# Create doctor schedules and time slots
def create_schedule_for_doctor(doctor):
    created_schedules = []
    
    # Create schedules for weekdays (Monday to Friday)
    for day in range(0, 5):  # 0=Monday, 4=Friday
        schedule, created = DoctorSchedule.objects.get_or_create(
            doctor=doctor,
            day_of_week=day,
            defaults={'is_available': True}
        )
        
        # Get day name
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_name = day_names[day]
        
        if created:
            created_schedules.append(f"Created schedule for {doctor.user.first_name} {doctor.user.last_name} on {day_name}")
        else:
            created_schedules.append(f"Schedule already exists for {doctor.user.first_name} {doctor.user.last_name} on {day_name}")
        
        # Add time slots (only if newly created to avoid duplicates)
        if created:
            # Morning slots
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(9, 0), end_time=time(9, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(9, 30), end_time=time(10, 0))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(10, 0), end_time=time(10, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(10, 30), end_time=time(11, 0))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(11, 0), end_time=time(11, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(11, 30), end_time=time(12, 0))
            
            # Afternoon slots
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(14, 0), end_time=time(14, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(14, 30), end_time=time(15, 0))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(15, 0), end_time=time(15, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(15, 30), end_time=time(16, 0))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(16, 0), end_time=time(16, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(16, 30), end_time=time(17, 0))
            
            created_schedules.append(f"Added 12 time slots to {day_name}")
    
    # Add some weekend availability for certain doctors (only Saturday)
    if doctor.id % 2 == 0:  # Every other doctor works on Saturday
        day = 5  # 5=Saturday
        day_name = 'Saturday'
        
        schedule, created = DoctorSchedule.objects.get_or_create(
            doctor=doctor,
            day_of_week=day,
            defaults={'is_available': True}
        )
        
        if created:
            created_schedules.append(f"Created schedule for {doctor.user.first_name} {doctor.user.last_name} on {day_name}")
            
            # Add limited Saturday slots (morning only)
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(9, 0), end_time=time(9, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(9, 30), end_time=time(10, 0))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(10, 0), end_time=time(10, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(10, 30), end_time=time(11, 0))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(11, 0), end_time=time(11, 30))
            TimeSlot.objects.create(doctor_schedule=schedule, start_time=time(11, 30), end_time=time(12, 0))
            
            created_schedules.append(f"Added 6 time slots to {day_name}")
        else:
            created_schedules.append(f"Schedule already exists for {doctor.user.first_name} {doctor.user.last_name} on {day_name}")
    
    return created_schedules

# Add schedules for all doctors
try:
    with transaction.atomic():
        doctors = Doctor.objects.all()
        print(f"Found {doctors.count()} doctors")
        
        all_messages = []
        for doctor in doctors:
            print(f"\nCreating schedules for {doctor.user.first_name} {doctor.user.last_name}...")
            messages = create_schedule_for_doctor(doctor)
            all_messages.extend(messages)
        
        # Print summary
        for message in all_messages:
            print(message)
        
        # Print schedule and slot count
        schedule_count = DoctorSchedule.objects.count()
        slot_count = TimeSlot.objects.count()
        print(f"\nTotal schedules created: {schedule_count}")
        print(f"Total time slots created: {slot_count}")
except Exception as e:
    print(f"Error creating schedules: {str(e)}")