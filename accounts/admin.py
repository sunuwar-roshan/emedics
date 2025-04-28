from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

# Register CustomUser model
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_staff', 'is_active']
    list_filter = ['user_type', 'is_staff', 'is_active']
    search_fields = ['username', 'email']
    ordering = ['username']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User type', {'fields': ('user_type',)}),  # Add user_type here
        ('Doctor-Specific fields', {'fields':('specialization','license_number')}),
        ('Patient-Specific fields', {'fields': ('date_of_birth', 'gender', 'emergency_contact_number')}),
        ('Extra info', {'fields': ('photo', 'phone','city','street_address')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'email', 'user_type', 'is_staff', 'is_active'),
        }),
    )
    
# Register your custom user model
admin.site.register(CustomUser, CustomUserAdmin) 
