from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth import logout
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
import random

from .forms import CustomUserCreationForm, ProfileEditForm
from appointments.models import Appointment

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_type = request.POST.get('user_type')  # Get user type from the login form

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user:
            # Ensure the user type provided in login matches the stored user type
            if user.user_type != user_type:
                messages.error(request, "Incorrect user type! Please select the correct role.")
                return render(request, 'accounts/login.html')
                # return redirect('login')

            login(request, user)

            # Redirect based on user type
            if user.is_authenticated:
                if user.user_type == 'doctor':
                    return redirect('doctor_dashboard')
                elif user.user_type == 'patient':
                    return redirect('patient_dashboard')

        else:
            messages.error(request, "Invalid credentials!")

    return render(request, 'accounts/login.html')

def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST,request.FILES)
        if form.is_valid():
            user_type = form.cleaned_data.get('user_type')

            # Validate user type
            if user_type not in ['doctor', 'patient']:
                messages.error(request, "Invalid user type selected.")
                return render(request, 'accounts/register.html', {'form': form})

            # Save user
            user = form.save(commit=False)
            user.user_type = user_type
            user.save()

            #   # Save additional fields
            # user.user_type = form.cleaned_data['user_type']
            # user.phone = form.cleaned_data['phone']
            # user.street_address = form.cleaned_data['street_address']
            # user.city = form.cleaned_data['city']
            # # user.photo = form.cleaned_data['photo']
            #   # Save image
            # if 'photo' in request.FILES:
            #     user.photo = request.FILES['photo']

            # # Save Doctor-specific fields
            # if user.user_type == 'doctor':
            #     user.specialization = form.cleaned_data['specialization']
            #     user.license_number = form.cleaned_data['license_number']

            # # Save Patient-specific fields
            # if user.user_type == 'patient':
            #     user.date_of_birth = form.cleaned_data['date_of_birth']
            #     user.gender = form.cleaned_data['gender']
            #     user.emergency_contact_number = form.cleaned_data['emergency_contact_number']

            # user.save()


            messages.success(request, "Registration successful. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

def doctor_dashboard(request):
    return render(request, 'accounts/doctor_dashboard.html')

def patient_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get upcoming appointments (today and future)
    upcoming_appointments = Appointment.objects.filter(
        patient_email=request.user.email,
        appointment_date__gte=timezone.now().date(),
        status='scheduled'  # Only show confirmed appointments
    ).order_by('appointment_date', 'time_slot')[:5]  # Limit to 5 upcoming
    
    # Get recent activities (appointments from last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_activities = Appointment.objects.filter(
        patient_email=request.user.email,
        appointment_date__gte=thirty_days_ago
    ).order_by('-appointment_date', '-time_slot')[:5]
    
    # List of 10 health tips
    all_health_tips = [
        {
            'title': 'Stay Hydrated',
            'description': 'Drink at least 8 glasses of water daily to maintain proper hydration and support body functions.',
            'category': 'Hydration'
        },
        {
            'title': 'Regular Exercise',
            'description': 'Aim for at least 30 minutes of moderate exercise most days of the week.',
            'category': 'Fitness'
        },
        {
            'title': 'Balanced Diet',
            'description': 'Include a variety of fruits, vegetables, and whole grains in your meals.',
            'category': 'Nutrition'
        },
        {
            'title': 'Adequate Sleep',
            'description': 'Get 7-9 hours of quality sleep each night for optimal health.',
            'category': 'Wellness'
        },
        {
            'title': 'Stress Management',
            'description': 'Practice meditation or deep breathing exercises to reduce stress.',
            'category': 'Mental Health'
        },
        {
            'title': 'Regular Check-ups',
            'description': 'Schedule regular health check-ups and screenings as recommended.',
            'category': 'Prevention'
        },
        {
            'title': 'Hand Hygiene',
            'description': 'Wash your hands frequently to prevent the spread of germs.',
            'category': 'Hygiene'
        },
        {
            'title': 'Limit Sugar Intake',
            'description': 'Reduce consumption of sugary drinks and snacks for better health.',
            'category': 'Nutrition'
        },
        {
            'title': 'Stay Active',
            'description': 'Take short breaks to stand and move if you sit for long periods.',
            'category': 'Fitness'
        },
        {
            'title': 'Mindful Eating',
            'description': 'Eat slowly and pay attention to your food to prevent overeating.',
            'category': 'Nutrition'
        }
    ]
    
    # Select 3 random health tips
    health_tips = random.sample(all_health_tips, min(3, len(all_health_tips)))
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'recent_activities': recent_activities,
        'upcoming_count': upcoming_appointments.count(),
        'medical_records_count': 3,  # Placeholder
        'active_medications_count': 2,  # Placeholder
        'test_results_count': 1,  # Placeholder
        'health_metrics': {
            'last_bp': '120/80 mmHg',
            'last_weight': '68 kg',
            'last_glucose': '95 mg/dL',
            'last_visit': '2025-05-15'
        },
        'quick_actions': [
            {'icon': 'calendar-plus', 'title': 'Book Appointment', 'url': 'create_appointment', 'enabled': True},
            {'icon': 'file-prescription', 'title': 'Request Refill', 'url': '#', 'enabled': False},
            {'icon': 'video', 'title': 'Start Telehealth', 'url': '#', 'enabled': False},
            {'icon': 'envelope', 'title': 'Message Doctor', 'url': '#', 'enabled': False},
        ],
        'health_tips': health_tips  # Add health tips to context
    }
    
    return render(request, 'accounts/patient_dashboard.html', context)

@login_required
def profile_settings(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_settings')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/profile_settings.html', {'form': form})

def home(request):
    return render(request, 'home/home.html')

def user_logout(request):
    logout(request)
    return redirect('home')  # Ensure 'home' is defined in your urls.py
