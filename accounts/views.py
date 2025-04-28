from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm
from django.contrib.auth import logout

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
    return render(request, 'accounts/patient_dashboard.html')

def home(request):
    return render(request, 'home/home.html')

def user_logout(request):
    logout(request)
    return redirect('home')  # Ensure 'home' is defined in your urls.py

