from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.utils import timezone
from .models import MedicalRecord
from django.db.models import Q
from .models import Appointment
from .forms import AppointmentForm
from accounts.models import CustomUser
from django.contrib.auth.decorators import login_required
import requests
from django.views.decorators.http import require_http_methods
import json
from .khalti_config import KHALTI_PUBLIC_KEY, APPOINTMENT_AMOUNT, KHALTI_SECRET_KEY


class AppointmentCreateView(CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/create_appointment.html'
    
    def form_valid(self, form):
        # Save appointment with pending payment status
        self.object = form.save(commit=False)
        self.object.payment_status = 'pending'
        self.object.save()
        
        # Redirect to payment view
        return redirect('appointment_payment', appointment_id=self.object.id)

def payment_view(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    context = {
        'appointment': appointment,
        'AMOUNT': APPOINTMENT_AMOUNT,  # This will be 1000 (Rs. 10 in paisa)
        # 'KHALTI_PUBLIC_KEY': KHALTI_PUBLIC_KEY,
        'KHALTI_PUBLIC_KEY': "36ae31f9f7f8474c805d47115d103c68",
    }
    return render(request, 'appointments/payment.html', context)

def appointment_success(request):
    return render(request, 'appointments/appointment_success.html')


@csrf_exempt
@require_http_methods(["POST"])
def verify_payment(request):
    if request.method == "POST":
        token = request.POST.get("token")
        amount = request.POST.get("amount")
        
        url = "https://test-api.khalti.com/v2/epayment/verify/"  # Test sandbox URL
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": f"Key {KHALTI_SECRET_KEY}"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # Payment successful
            appointment_id = request.POST.get("appointment_id")
            appointment = Appointment.objects.get(id=appointment_id)
            appointment.payment_status = 'completed'
            appointment.save()
            return JsonResponse({"status": "success"})
        
        return JsonResponse({"status": "failed"})

@method_decorator(csrf_exempt, name='dispatch')
class GetDoctorsView(View):
    """AJAX view to get doctors based on specialization"""
    def post(self, request):
        specialization = request.POST.get('specialization')
        # In a real app, you'd query doctors by specialization
        # This is a simplified example with hardcoded data
        doctors = {
            'cardiology': ['Dr. John Smith', 'Dr. Sarah Johnson'],
            'dermatology': ['Dr. Michael Brown', 'Dr. Emily Davis'],
            'neurology': ['Dr. Robert Wilson', 'Dr. Jennifer Thompson'],
            # Add more specializations and doctors as needed
        }
        
        doctor_list = doctors.get(specialization, [])
        return JsonResponse({'doctors': doctor_list})


# For checking appointment availability
class CheckAvailabilityView(View):
    """AJAX view to check appointment availability"""
    def post(self, request):
        doctor = request.POST.get('doctor')
        date = request.POST.get('date')
        
        # Query for existing appointments
        booked_slots = Appointment.objects.filter(
            doctor_name=doctor,
            appointment_date=date
        ).values_list('time_slot', flat=True)
        
        # All possible time slots from model
        all_slots = [slot[0] for slot in Appointment.TIME_SLOTS]
        
        # Available slots are those not booked
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return JsonResponse({'available_slots': available_slots})


class AppointmentHistoryView(LoginRequiredMixin, ListView):
    """Class-based view to display appointment history for the logged-in user only"""
    model = Appointment
    template_name = 'appointments/appointment_history.html'
    context_object_name = 'appointments'
    paginate_by = 10  # Optional: adds pagination
    
    def get_queryset(self):
        """Filter appointments to show only those for the logged-in user"""
        return Appointment.objects.filter(
            main_user = self.request.user.id
        ).order_by('-appointment_date', '-time_slot')


class DoctorAppointmentsView(LoginRequiredMixin, ListView):
    """Class-based view to display appointments for the logged-in doctor only"""
    model = Appointment
    template_name = 'appointments/appointments_doctor.html'
    context_object_name = 'all_appointments'
    
    def get_queryset(self):
        """Filter appointments to show only those for the logged-in doctor"""
        # Get the doctor's username or full name
        doctor_identifier = self.request.user.username
        
        # Filter appointments where doctor_name matches the current user's name
        return Appointment.objects.filter(
            doctor_name=doctor_identifier
        ).order_by('appointment_date', 'time_slot')
    
    def get_context_data(self, **kwargs):
        """Add extra context data for the different appointment categories"""
        context = super().get_context_data(**kwargs)
        
        # Get all appointments from the queryset
        all_appointments = self.get_queryset()
        context['all_appointments'] = all_appointments
        
        # Get current date
        today = timezone.now().date()
        
        # Today's appointments
        context['today_appointments'] = all_appointments.filter(
            appointment_date=today
        )
       
        
        # Upcoming appointments (future dates)
        context['upcoming_appointments'] = all_appointments.filter(
            appointment_date__gt=today
        )
        
        # Past appointments (completed or dates in the past)
        context['past_appointments'] = all_appointments.filter(
            appointment_date__lt=today
        )
        
        # Cancelled appointments (if you have a status field)
        if 'status' in [f.name for f in Appointment._meta.get_fields()]:
            context['cancelled_appointments'] = all_appointments.filter(
                status='cancelled'
            )
        else:
            context['cancelled_appointments'] = []
        
        # Count stats
        context['today_count'] = context['today_appointments'].count()
        context['upcoming_count'] = context['upcoming_appointments'].count()
        context['pending_count'] = 0  # Update this if you have a 'pending' status
        
        # Count unique patients
        patient_emails = all_appointments.values_list('patient_email', flat=True).distinct()
        # context['total_patients'] = len(patient_emails)
        print(f"Total unique patients: {len(patient_emails)}")
        context['total_patients'] = len(patient_emails)
        # print(f"Total unique patients: {context['total_patients']}")
        # print(f"Today's patients count: {context['total_patients']}")
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Prevent non-doctors from accessing this view"""
        if request.user.is_authenticated and request.user.user_type != 'doctor':
            messages.error(request, "Access denied. Only doctors can view this page.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)


def view_appointment(request, appointment_id):
    """View to display detailed information about an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if this doctor has permission to view this appointment
    if request.user.username != appointment.doctor_name and request.user.user_type == 'doctor':
        messages.error(request, "You don't have permission to view this appointment.")
        return redirect('doctor_appointments')
    
    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment
    })


def complete_appointment(request, appointment_id):
    """Mark an appointment as completed"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if this doctor has permission to update this appointment
    if request.user.username != appointment.doctor_name and request.user.user_type == 'doctor':
        messages.error(request, "You don't have permission to update this appointment.")
        return redirect('appointments_doctor')
    
    if request.method == 'POST':
        # Update appointment status
        appointment.status = 'completed'
        
        # Add notes if provided
        if 'notes' in request.POST and request.POST['notes']:
            appointment.notes = request.POST['notes']
        
        # Save the changes
        appointment.save()
        
        messages.success(request, "Appointment marked as completed successfully.")
        return redirect('appointments_doctor')
    
    # If GET request, show the form
    return render(request, 'appointments/complete_appointment.html', {
        'appointment': appointment
    })


def cancel_appointment(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check if this doctor has permission to cancel this appointment
    if request.user.username != appointment.doctor_name and request.user.user_type == 'doctor':
        messages.error(request, "You don't have permission to cancel this appointment.")
        return redirect('doctor_appointments')
    
    if request.method == 'POST':
        # Update appointment status
        appointment.status = 'cancelled'
        
        # Add cancellation reason if provided
        if 'reason' in request.POST and request.POST['reason']:
            appointment.notes = f"Cancelled by doctor. Reason: {request.POST['reason']}"
        
        # Save the changes
        appointment.save()
        
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('appointments_doctor')
    
    # If GET request, show the cancellation form
    return render(request, 'appointments/cancel_appointment.html', {
        'appointment': appointment
    })

def reschedule_appointment(request, appointment_id):
    """Reschedule an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permission
    if request.user.username != appointment.doctor_name and request.user.user_type == 'doctor':
        messages.error(request, "You don't have permission to reschedule this appointment.")
        return redirect('appointments_doctor')
    
    if request.method == 'POST':
        # Get form data
        new_date = request.POST.get('appointment_date')
        display_time = request.POST.get('time_slot')  # This is the display value
        reason = request.POST.get('reason')
        
        # Convert display time to time slot key
        time_slot_key = None
        for key, value in Appointment.TIME_SLOTS:
            if value == display_time:
                time_slot_key = key
                break
        
        # If no matching key found
        if not time_slot_key:
            messages.error(request, "Invalid time slot selection.")
            return redirect('reschedule_appointment', appointment_id=appointment_id)
        
        # Update appointment with key instead of display value
        appointment.appointment_date = new_date
        appointment.time_slot = time_slot_key
        
        # Add reason if provided
        if reason:
            appointment.notes = f"Rescheduled by doctor. Reason: {reason}"
        
        appointment.save()
        
        messages.success(request, "Appointment rescheduled successfully.")
        return redirect('appointments_doctor')
    
    # For GET requests
    # Get available time slots for display in the form
    available_slots = [display for key, display in Appointment.TIME_SLOTS]
    
    return render(request, 'appointments/reschedule_appointment.html', {
        'appointment': appointment,
        'available_slots': available_slots
    })



def doctor_dashboard(request):
    """View function for the doctor dashboard"""
    # Check if user is a doctor
    if request.user.user_type != 'doctor':
        messages.error(request, "Access denied. This dashboard is for doctors only.")
        return redirect('home')
    
    # Get the logged-in doctor's identifier
    doctor_identifier = request.user.username
    
    # Debug: Print the doctor's username to check what we're filtering by
    # print(f"Looking for appointments with doctor_name: {doctor_identifier}")
    
    # Get current date
    today = timezone.now().date()
    
    # Debug: Get ALL appointments to check what's in the database
    all_appointments_debug = Appointment.objects.all()
    # print(f"Total appointments in system: {all_appointments_debug.count()}")
    # print(f"Doctor names in database: {list(all_appointments_debug.values_list('doctor_name', flat=True).distinct())}")
    
    # Get all appointments for this doctor
    all_appointments = Appointment.objects.filter(
    doctor_name__icontains=request.user.username.split()[0]  # Match partial name, case-insensitive
)
    
    # Today's appointments
    
    today_appointments = all_appointments.filter(appointment_date=today)
    # print(f"Today's appointments for {doctor_identifier}: {today_appointments.count()}")
    past_appointments = Appointment.objects.filter(appointment_date__lt=today)
    # print(f"Past appointments for {doctor_identifier}: {past_appointments}")
    # Past appointments (completed or dates in the past)
    # context['past_appointments'] = all_appointments.filter(
#             appointment_date__lt=today
#     )
    
    # Upcoming appointments (future dates)
    upcoming_appointments = all_appointments.filter(appointment_date__gt=today)
    
    # Get appointment counts
    today_count = today_appointments.count()
    upcoming_count = upcoming_appointments.count()
    pending_count = all_appointments.filter(status='pending').count()
    total_patients = all_appointments.values('patient_email').distinct().count()
    print(f"total patients: {total_patients}")
    # print(f"Total patients for {doctor_identifier}: {total_patients}")
    # Rest of your code...
    
    context = {
        'today_appointments': today_appointments,
        'today_count': today_count,
        'upcoming_count': upcoming_count,
        'pending_count': pending_count,
        'total_patients': total_patients,
        'past_appointments': past_appointments,
        # ...other context variables
    }
    
    return render(request, 'accounts/doctor_dashboard.html', context)

class DoctorMedicalRecordsView(LoginRequiredMixin, ListView):
    model = MedicalRecord
    template_name = 'appointments/doctor_medical_records.html'
    context_object_name = 'medical_records'
    paginate_by = 10
    
    def get_queryset(self):
        # Get base queryset - only records from patients this doctor has treated
        queryset = MedicalRecord.objects.filter(doctor=self.request.user)
        
        # Apply filters from request
        patient_search = self.request.GET.get('patient_search')
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if patient_search:
            queryset = queryset.filter(
                Q(patient_name__icontains=patient_search) | 
                Q(patient_email__icontains=patient_search)
            )
            
        if date_from:
            queryset = queryset.filter(date_created__gte=date_from)
            
        if date_to:
            queryset = queryset.filter(date_created__lte=date_to)
        
        return queryset.order_by('-date_created')
    
    @login_required
    def complete_appointment(request, appointment_id):
        """Mark an appointment as completed and create a medical record"""
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check if this doctor has permission to update this appointment
        if appointment.doctor_name != request.user.username and request.user.is_doctor:
            messages.error(request, "You don't have permission to update this appointment.")
            return redirect('appointments_doctor')
        
        if request.method == 'POST':
            # Update appointment status
            appointment.status = 'completed'
            
            # Add notes if provided
            if 'notes' in request.POST and request.POST['notes']:
                appointment.notes = request.POST['notes']
            
            # Save the changes
            appointment.save()
            
            # Create a medical record if checkbox is checked
            if 'create_medical_record' in request.POST:
                # Find the patient user
                patient = CustomUser.objects.filter(email=appointment.patient_email).first()
                
                # Create the medical record
                medical_record = MedicalRecord(
                    patient=patient,
                    doctor=request.user,
                    patient_name=appointment.patient_name,
                    patient_email=appointment.patient_email,
                    diagnosis=request.POST.get('diagnosis', ''),
                    treatment=request.POST.get('treatment', ''),
                    notes=request.POST.get('medical_notes', appointment.notes),
                    status='active'
                )
                medical_record.save()
                
                messages.success(request, "Appointment marked as completed and medical record created successfully.")
            else:
                messages.success(request, "Appointment marked as completed successfully.")
            
            return redirect('appointments_doctor')
        
        # If GET request, show the form
        return render(request, 'appointments/complete_appointment.html', {
            'appointment': appointment
        })

from django.shortcuts import render
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Count

from accounts.models import CustomUser
from .models import Appointment, MedicalRecord

def home(request):
    """Home page view with dashboard statistics"""
    today = timezone.now().date()
    
    # Get today's appointments
    daily_appointments = Appointment.objects.filter(
        appointment_date=today
    ).count()
    
    # Get total patients (users with 'patient' user type)
    total_patients = CustomUser.objects.filter(
        user_type='patient'
    ).count()
    
    # Get total doctors (users with 'doctor' user type)
    total_doctors = CustomUser.objects.filter(
        user_type='doctor'
    ).count()
    
    # Get total specializations/departments
    total_specializations = Appointment.objects.values('specialization').distinct().count()
    
    # Get upcoming appointments for this week
    one_week_later = today + timedelta(days=7)
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today,
        appointment_date__lte=one_week_later,
        status='scheduled'
    ).order_by('appointment_date', 'time_slot')[:5]  # Limit to 5 for display
    
    # Get recent appointments
    recent_appointments = Appointment.objects.filter(
        status='completed'
    ).order_by('-appointment_date', '-time_slot')[:5]  # Most recent first, limit to 5
    
    # Current ER wait time (simulated - you would replace this with actual data if available)
    current_er_wait = 15
    
    # Available beds (simulated - you would replace this with actual data if available)
    available_beds = 43
    total_beds = 120
    
    # Surgeries today (simulated - you would replace this with actual data if available)
    surgeries_today = 12
    
    # Staff on duty (simulated - you would replace this with actual data if available)
    staff_on_duty = 78
    
    context = {
        'daily_appointments': daily_appointments,
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_specializations': total_specializations,
        'upcoming_appointments': upcoming_appointments,
        'recent_appointments': recent_appointments,
        'current_er_wait': current_er_wait,
        'available_beds': available_beds,
        'total_beds': total_beds,
        'surgeries_today': surgeries_today,
        'staff_on_duty': staff_on_duty,
    }
    
    return render(request, 'home/home.html', context)