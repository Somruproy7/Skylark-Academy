from functools import reduce
from operator import or_
import requests

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout as auth_logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist

from .models import Module, Student, Registration, Course
from .forms import UserRegistrationForm, StudentProfileForm, ContactForm, ModuleSearchForm

def home(request):
    """Home page with featured modules"""
    featured_modules = Module.objects.filter(availability=True)[:6]
    context = {
        'featured_modules': featured_modules,
    }
    return render(request, 'registration/home.html', context)

def about(request):
    """About page"""
    return render(request, 'registration/about.html')

def contact(request):
    """Contact page with form"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # In a real application, you would send an email here
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()
    
    context = {'form': form}
    return render(request, 'registration/contact.html', context)

def register_user(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save user with proper role flags
            user = form.save(commit=False)
            user.is_student = True
            user.is_teacher = False  # Explicitly set to False for student registration
            user.save()
            
            # Add user to Students group
            students_group, _ = Group.objects.get_or_create(name='Students')
            user.groups.add(students_group)
            
            # Create student profile with default values
            Student.objects.create(
                user=user,
                student_id=f"STU{user.id:05d}",  # Generate a student ID
                date_of_birth='2000-01-01',
                address='',
                city='',
                country='',
                # Note: course will need to be set later in profile completion
            )
            
            # Log the user in
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            
            messages.success(request, 'Registration successful! Please complete your profile and select your course.')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    
    context = {'form': form}
    return render(request, 'registration/register.html', context)

@login_required
def modules(request):
    """Modules listing with search and pagination"""
    modules_list = Module.objects.filter(availability=True)
    
    # Search functionality
    search_form = ModuleSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        category = search_form.cleaned_data.get('category')
        course = search_form.cleaned_data.get('course')
        
        if search:
            # Use a list of Q objects with OR conditions
            search_conditions = [
                Q(name__icontains=search),
                Q(code__icontains=search),
                Q(description__icontains=search)
            ]
            combined_query = reduce(or_, search_conditions)  # type: ignore[operator]
            modules_list = modules_list.filter(combined_query)
        
        if category:
            modules_list = modules_list.filter(category=category)
        
        if course:
            modules_list = modules_list.filter(courses=course)
    
    # Filter modules based on student's course if authenticated
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            # Show modules that are available for the student's course
            # If student has a course, filter modules that are either:
            # 1. Available for all courses (no course restrictions)
            # 2. Available for the student's specific course
            if student.course:
                modules_list = modules_list.filter(
                    Q(courses__isnull=True) | Q(courses=student.course)
                ).distinct()
        except ObjectDoesNotExist:
            pass
    
    # Pagination
    paginator = Paginator(modules_list, 10)
    page_number = request.GET.get('page')
    modules_page = paginator.get_page(page_number)
    
    # Check if user is registered for each module and if they can register
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            registered_modules = Registration.objects.filter(student=student).values_list('module_id', flat=True)
            for module in modules_page:
                module.is_registered = module.id in registered_modules
                # Check if student can register (must have a course)
                module.can_register = student.course is not None
        except ObjectDoesNotExist:
            for module in modules_page:
                module.is_registered = False
                module.can_register = False
    
    context = {
        'modules': modules_page,
        'search_form': search_form,
    }
    return render(request, 'registration/modules.html', context)

import logging

logger = logging.getLogger(__name__)

def module_detail(request, module_code):
    """Module detail page showing module info and registered students"""
    module = get_object_or_404(Module, code=module_code)
    
    # Get registered students with their photos
    registrations = Registration.objects.filter(module=module, status='A').select_related('student__user')
    
    # Check if current user is registered
    is_registered = False
    can_register = False
    if request.user.is_authenticated:
        try:
            student = Student.objects.get(user=request.user)
            is_registered = Registration.objects.filter(student=student, module=module).exists()
            
            # Check if student can register (module available for their course)
            if student.course:
                # Allow registration if:
                # 1. Module has no course restrictions (empty courses list) - allow all students
                # 2. Module has course restrictions and student's course is in the allowed list
                module_courses = list(module.courses.values_list('id', flat=True))
                can_register = (not is_registered and module.availability and 
                              ((len(module_courses) == 0) or (student.course.id in module_courses)))
                
                # Log the registration check for debugging
                logger.info(f"[MODULE_DETAIL] Student {student.pk} can register for {module.code}: {can_register}")
                logger.info(f"[MODULE_DETAIL] Module courses: {module_courses}")
                logger.info(f"[MODULE_DETAIL] Student course: {student.course.id}")
                logger.info(f"[MODULE_DETAIL] Module has no restrictions: {len(module_courses) == 0}")
                logger.info(f"[MODULE_DETAIL] Student course in allowed courses: {student.course.id in module_courses}")
                
        except ObjectDoesNotExist:
            logger.warning(f"[MODULE_DETAIL] No student profile for user {request.user}")
            pass
    
    context = {
        'module': module,
        'registrations': registrations,
        'is_registered': is_registered,
        'can_register': can_register,
        'available_slots': module.courses_allowed - registrations.count(),
    }
    return render(request, 'registration/module_detail.html', context)

@login_required
def profile(request):
    """User profile view"""
    try:
        student = Student.objects.select_related('course').get(user=request.user)
        registrations = Registration.objects.filter(student=student, status='A').select_related('module')
        # Only show course modules if student is enrolled in a course
        course_modules = None
        if student.course:
            course_modules = Module.objects.filter(
                Q(courses=student.course) | Q(courses__isnull=True),
                availability=True
            ).exclude(registrations__student=student)
    except ObjectDoesNotExist:
        student = None
        registrations = []
        course_modules = None
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'update_personal_details' in request.POST:
            # Update personal details only (excludes course and enrollment)
            from .forms import StudentPersonalDetailsForm
            form = StudentPersonalDetailsForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                student = form.save(commit=False)
                student.user = request.user
                # Preserve existing course and enrollment data
                if student.pk:
                    original_student = Student.objects.get(pk=student.pk)
                    student.course = original_student.course
                    student.enrollment_date = original_student.enrollment_date
                    student.expected_graduation = original_student.expected_graduation
                student.save()
                messages.success(request, 'Personal details updated successfully!')
                return redirect('profile')
        else:
            # Update course enrollment (full profile form)
            from .forms import StudentProfileForm
            form = StudentProfileForm(request.POST, request.FILES, instance=student)
            if form.is_valid():
                student = form.save(commit=False)
                student.user = request.user
                student.save()
                messages.success(request, 'Course enrollment updated successfully!')
                return redirect('profile')
    else:
        # Show appropriate forms based on whether student has a course
        from .forms import StudentPersonalDetailsForm, StudentProfileForm
        personal_form = StudentPersonalDetailsForm(instance=student)
        course_form = StudentProfileForm(instance=student)
    
    context = {
        'student': student,
        'personal_form': personal_form,
        'course_form': course_form,
        'registrations': registrations,
        'course_modules': course_modules,
    }
    return render(request, 'registration/profile.html', context)

import logging

logger = logging.getLogger(__name__)

@login_required
@require_http_methods(["POST"])
def register_module(request, module_code):
    """Register for a module"""
    try:
        logger.info(f"[REGISTER_MODULE] Starting registration for user {request.user} and module {module_code}")
        
        # Get the module
        try:
            module = Module.objects.get(code=module_code)
            logger.info(f"[REGISTER_MODULE] Found module: {module.code} - {module.name}")
        except ObjectDoesNotExist:
            error_msg = f"Module {module_code} not found"
            logger.error(f"[REGISTER_MODULE] {error_msg}")
            messages.error(request, 'Module not found.')
            return redirect('modules')
        
        # Check if student profile exists
        try:
            student = request.user.student_profile
            logger.info(f"[REGISTER_MODULE] Found student profile - User: {student.user.username}")
            logger.info(f"[REGISTER_MODULE] Student course: {getattr(student, 'course', 'No course assigned')}")
            logger.info(f"[REGISTER_MODULE] Student object: {student}")
            
            # Ensure student has a course
            if not student.course:
                messages.error(request, 'You must be enrolled in a course before registering for modules.')
                return redirect('courses')
        except ObjectDoesNotExist:
            error_msg = f"Student profile not found for user {request.user}"
            logger.error(f"[REGISTER_MODULE] {error_msg}")
            messages.error(request, 'Student profile not found. Please complete your profile first.')
            return redirect('profile')
        
        # Check if already registered
        existing_reg = Registration.objects.filter(student=student, module=module).first()
        if existing_reg:
            logger.warning(f"[REGISTER_MODULE] User {request.user} already registered for module {module.code} with status {existing_reg.get_status_display()}")
            if existing_reg.status == 'A':
                messages.warning(request, f'You are already registered for {module.name}')
            elif existing_reg.status == 'P':
                # Update to approved status
                existing_reg.status = 'A'
                existing_reg.save()
                messages.success(request, f'Your registration for {module.name} has been approved!')
                return redirect('modules')
            elif existing_reg.status == 'W':
                # Update to approved status
                existing_reg.status = 'A'
                existing_reg.save()
                messages.success(request, f'You have been moved from waiting list to approved for {module.name}!')
                return redirect('modules')
            elif existing_reg.status == 'R':
                # Allow re-registration if previously rejected
                existing_reg.status = 'A'
                existing_reg.save()
                messages.success(request, f'Successfully re-registered for {module.name}!')
                return redirect('modules')
            elif existing_reg.status == 'D':
                # Allow re-registration if previously dropped
                existing_reg.status = 'A'
                existing_reg.save()
                messages.success(request, f'Successfully re-registered for {module.name}!')
                return redirect('modules')
            else:
                messages.warning(request, f'You have a registration for {module.name} with status: {existing_reg.get_status_display()}')
            return redirect('modules')
        
        # Check if module has available spots
        current_registrations = Registration.objects.filter(module=module).count()
        logger.info(f"[REGISTER_MODULE] Current registrations for {module.code}: {current_registrations}/{module.courses_allowed}")
        
        if current_registrations >= module.courses_allowed:
            logger.warning(f"[REGISTER_MODULE] Module {module.code} is full")
            messages.error(request, f'Sorry, {module.name} is full.')
            return redirect('modules')
        
        # Check student's course and module relationship
        student_course = getattr(student, 'course', None)
        if not student_course:
            error_msg = f"Student {student.id} has no course assigned"
            logger.error(f"[REGISTER_MODULE] {error_msg}")
            messages.error(request, 'You are not enrolled in any course. Please contact support.')
            return redirect('modules')
        
        # Check if module is available for student's course
        module_courses = list(module.courses.values_list('id', flat=True))
        logger.info(f"[REGISTER_MODULE] Module {module.code} is available for courses: {module_courses}")
        
        # Allow registration if:
        # 1. Module has no course restrictions (empty courses list) - allow all students
        # 2. Module has course restrictions and student's course is in the allowed list
        can_register_for_module = (len(module_courses) == 0) or (student_course.id in module_courses)
        
        if not can_register_for_module:
            error_msg = f"Module {module.code} not available for student's course {student_course.name} (ID: {student_course.id})"
            logger.warning(f"[REGISTER_MODULE] {error_msg}")
            messages.error(request, 
                f'You cannot register for {module.name} as it is not available for your course ({student_course.name}). '
                f'Please contact your academic advisor if you believe this is an error.'
            )
            return redirect('modules')
        
        # Create registration with transaction
        logger.info(f"[REGISTER_MODULE] Attempting to create registration for student {student.user.username} and module {module.code}")
        
        # Create and validate the registration object
        registration = Registration(
            student=student, 
            module=module, 
            status='A'  # Approved status
        )
        
        try:
            logger.info("[REGISTER_MODULE] Validating registration data...")
            registration.full_clean()
            
            # Start a transaction
            sid = transaction.savepoint()
            try:
                # Save the registration
                registration.save(force_insert=True)
                logger.info(f"[REGISTER_MODULE] Successfully created registration for student {student.user.username} and module {module.code}")
                
                # Get updated registration count
                current_registrations = Registration.objects.filter(module=module).count()
                logger.info(f"[REGISTER_MODULE] Updated registration count for {module.code}: {current_registrations}/{module.courses_allowed}")
                
                # Commit the transaction
                transaction.savepoint_commit(sid)
                messages.success(request, f'Successfully registered for {module.name}!')
                return redirect('modules')
                
            except Exception as e:
                # Rollback transaction on error
                transaction.savepoint_rollback(sid)
                raise
                
        except ValidationError as e:
            error_msg = f"Validation error during registration: {e}"
            logger.error(f"[REGISTER_MODULE] {error_msg}")
            logger.exception("Validation error details:")
            
            # More user-friendly error messages
            if 'student' in str(e):
                messages.error(request, 'There was an issue with your student profile. Please contact support.')
            elif 'module' in str(e):
                messages.error(request, 'There was an issue with the module selection. Please try again.')
            else:
                messages.error(request, 'Please check the registration details and try again.')
            
        except IntegrityError as e:
            error_msg = f"Database integrity error: {e}"
            logger.error(f"[REGISTER_MODULE] {error_msg}")
            logger.exception("Database error details:")
            
            if 'unique' in str(e).lower():
                # Check if there's already a registration
                existing_reg = Registration.objects.filter(student=student, module=module).first()
                if existing_reg:
                    if existing_reg.status == 'A':
                        messages.warning(request, 'You are already registered for this module.')
                    else:
                        messages.info(request, f'You have a {existing_reg.get_status_display().lower()} registration for this module.')
                else:
                    messages.error(request, 'There was an issue with your registration. Please try again.')
            else:
                messages.error(request, 'This module might be full or there was an issue with your registration. Please check your registrations.')
            
        except Exception as e:
            error_msg = f"Unexpected error during registration: {e}"
            logger.error(f"[REGISTER_MODULE] {error_msg}")
            logger.exception("Unexpected error details:")
            messages.error(request, 'An unexpected error occurred. Please try again later.')
        
    except Exception as e:
        error_msg = f"Unexpected error in register_module: {str(e)}"
        logger.error(f"[REGISTER_MODULE] {error_msg}")
        logger.exception("Full traceback:")
        messages.error(request, 'An unexpected error occurred. Please try again later.')
    
    return redirect('modules')

@login_required
@require_POST
def unregister_module(request, module_code):
    """Unregister from a module"""
    try:
        student = Student.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile')
    
    module = get_object_or_404(Module, code=module_code)
    registration = get_object_or_404(Registration, student=student, module=module)
    
    registration.delete()
    messages.success(request, f'Successfully unregistered from {module.name}')
    
    return redirect('modules')

@login_required
def my_registrations(request):
    """View showing all modules the student is registered in"""
    try:
        student = Student.objects.get(user=request.user)
        registrations = Registration.objects.filter(student=student).select_related('module').order_by('-registration_date')
    except ObjectDoesNotExist:
        registrations = []
        messages.warning(request, 'Please complete your profile first.')
        return redirect('profile')
    
    context = {
        'registrations': registrations,
        'student': student,
    }
    return render(request, 'registration/my_registrations.html', context)

# Course listing view
def courses(request):
    """Display all available courses"""
    courses_list = Course.objects.filter(is_active=True)
    context = {
        'courses': courses_list,
    }
    return render(request, 'registration/courses.html', context)

# Course enrollment view
@login_required
def enroll_course(request, course_code):
    """Enroll a student in a course"""
    try:
        student = Student.objects.get(user=request.user)
    except ObjectDoesNotExist:
        messages.error(request, 'Please complete your profile first.')
        return redirect('profile')
    
    course = get_object_or_404(Course, code=course_code, is_active=True)
    
    if student.course:
        messages.warning(request, f'You are already enrolled in {student.course.name}. You can only enroll in one course at a time.')
        return redirect('profile')
    
    # Enroll the student
    student.course = course
    student.save()
    
    messages.success(request, f'Successfully enrolled in {course.name}!')
    return redirect('profile')

# Course detail view
def course_detail(request, course_code):
    """Display detailed information about a specific course"""
    course = get_object_or_404(Course, code=course_code, is_active=True)
    
    # Get modules available for this course
    modules = Module.objects.filter(
        Q(courses=course) | Q(courses__isnull=True),
        availability=True
    )
    
    # Get students enrolled in this course
    students = course.students.filter(is_active=True)
    
    context = {
        'course': course,
        'modules': modules,
        'students': students,
    }
    return render(request, 'registration/course_detail.html', context)

def api_modules(request):
    """API endpoint for modules"""
    modules = Module.objects.filter(availability=True)
    data = []
    for module in modules:
        data.append({
            'id': module.id,
            'code': module.code,
            'name': module.name,
            'category': module.category,
            'credit': module.credit,
            'description': module.description,
            'courses_allowed': module.courses_allowed,
            'linked_courses': [course.code for course in module.courses.all()],
        })
    return JsonResponse({'modules': data})

def api_external_data(request):
    """Fetch external API data (example)"""
    try:
        # Example: Fetch some external data
        response = requests.get('https://jsonplaceholder.typicode.com/posts/1')
        if response.status_code == 200:
            return JsonResponse(response.json())
        else:
            return JsonResponse({'error': 'Failed to fetch external data'}, status=500)
    except requests.RequestException:
        return JsonResponse({'error': 'Network error'}, status=500)

def logout(request):
    """Custom logout view that redirects to home page"""
    auth_logout(request)
    return redirect('home')

