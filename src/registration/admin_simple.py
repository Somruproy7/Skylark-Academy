from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import Module, Student, Registration

User = get_user_model()

# Simple admin registrations to test
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'credit', 'availability']
    list_filter = ['category', 'availability']
    search_fields = ['code', 'name']

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user', 'city', 'country']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name']

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'module', 'status', 'registration_date']
    list_filter = ['status', 'registration_date']

# Custom User Admin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_student', 'is_teacher')
    list_filter = ('is_staff', 'is_student', 'is_teacher', 'is_active')

admin.site.register(User, UserAdmin)

# Set admin site headers
admin.site.site_header = 'University Registration System Admin'
admin.site.site_title = 'University Registration System'
admin.site.index_title = 'Welcome to the University Registration System'
