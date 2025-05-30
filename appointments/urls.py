from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.AppointmentCreateView.as_view(), name='create_appointment'),
    path('get-doctors/', views.GetDoctorsView.as_view(), name='get_doctors'),
    path('check-availability/', views.CheckAvailabilityView.as_view(), name='check_availability'),
    path('history/', views.AppointmentHistoryView.as_view(), name='appointment_history'),
    path('doctor/appointments/', views.DoctorAppointmentsView.as_view(), name='appointments_doctor'),
    path('appointment/<int:appointment_id>/', views.view_appointment, name='appointment_detail'),
    path('appointment/<int:appointment_id>/complete/', views.complete_appointment, name='complete_appointment'),
    path('appointment/<int:appointment_id>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/<int:appointment_id>/reschedule/', views.reschedule_appointment, name='reschedule_appointment'),
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor/medical-records/', views.DoctorMedicalRecordsView.as_view(), name='doctor_medical_records'),
    # path('medical-records/view/<int:pk>/', views.ViewMedicalRecordView.as_view(), name='view_medical_record'),
    # path('medical-records/edit/<int:pk>/', views.EditMedicalRecordView.as_view(), name='edit_medical_record'),
    path('create/', views.AppointmentCreateView.as_view(), name='create_appointment'),
    path('payment/<int:appointment_id>/', views.payment_view, name='appointment_payment'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    path('success/', views.appointment_success, name='appointment_success'),



]