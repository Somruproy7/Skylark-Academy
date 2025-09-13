from django import forms
from django.db import models  # type: ignore
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Student, Module, Course
from django.core.validators import RegexValidator

# Get the custom user model
User = get_user_model()

# Add type ignore to Course usage to suppress Pyright errors
# pyright: reportGeneralTypeIssues=error
# pyright: reportUnknownMemberType=false

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class StudentProfileForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=False)
    
    class Meta:
        model = Student
        fields = ['course', 'date_of_birth', 'address', 'city', 'country', 'photo', 'enrollment_date', 'expected_graduation']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_graduation': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active courses
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        self.fields['course'].empty_label = "Select a course"

# [NEW] Personal details update form (excludes course and enrollment)
class StudentPersonalDetailsForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=False)
    
    class Meta:
        model = Student
        fields = ['date_of_birth', 'gender', 'address', 'city', 'state', 'postal_code', 'country', 'phone', 'emergency_contact', 'emergency_phone', 'photo', 'bio']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make some fields required for personal details
        self.fields['date_of_birth'].required = True
        self.fields['city'].required = True
        self.fields['country'].required = True

# Enhanced Student Registration Form
class StudentRegistrationForm(forms.ModelForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = forms.CharField(validators=[phone_regex], max_length=17, required=False)
    
    class Meta:
        model = Student
        fields = [
            'course', 'date_of_birth', 'gender', 'address', 'city', 'state', 
            'postal_code', 'country', 'phone', 'emergency_contact', 
            'emergency_phone', 'photo', 'bio', 'enrollment_date', 'expected_graduation'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'enrollment_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_graduation': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active courses
        self.fields['course'].queryset = Course.objects.filter(is_active=True)
        self.fields['course'].empty_label = "Select a course"
        # Make course required
        self.fields['course'].required = True

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    subject = forms.CharField(max_length=200, required=True)
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5}), required=True)
    phone = forms.CharField(max_length=20, required=False)
    department = forms.ChoiceField(choices=[
        ('', 'Select Department'),
        ('admissions', 'Admissions'),
        ('academic', 'Academic Affairs'),
        ('student_services', 'Student Services'),
        ('technical', 'Technical Support'),
        ('general', 'General Inquiry'),
    ], required=True)

class ModuleSearchForm(forms.Form):
    search = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Search modules...'}))
    category = forms.ChoiceField(choices=[('', 'All Categories')] + Module.CATEGORY_CHOICES, required=False)
    course = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True), 
        required=False, 
        empty_label="All Courses",
        widget=forms.Select(attrs={'class': 'form-select'})
    ) 