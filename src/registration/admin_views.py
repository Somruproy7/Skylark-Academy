from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.paginator import Paginator
from .models import Module, Student, Registration, User, AdminAuditLog
import csv

def is_superuser(user):
    return user.is_superuser

@staff_member_required
def admin_dashboard(request):
    """Admin dashboard with statistics and overview"""
    
    # Get current date and time
    now = timezone.now()
    this_month = now.replace(day=1)
    
    # Basic statistics
    total_students = Student.objects.count()
    total_modules = Module.objects.count()
    total_registrations = Registration.objects.count()
    active_modules = Module.objects.filter(availability=True).count()
    
    # Recent activity
    recent_registrations = Registration.objects.select_related('student__user', 'module').order_by('-registration_date')[:10]
    recent_students = Student.objects.select_related('user').order_by('-created_at')[:5]
    
    # Module statistics
    module_stats = Module.objects.annotate(
        student_count=Count('registrations')
    ).order_by('-student_count')[:10]
    
    # Category distribution
    category_stats = Module.objects.values('category').annotate(
        count=Count('id'),
        avg_credit=Avg('credit')
    ).order_by('-count')
    
    # Registration status distribution
    status_stats = Registration.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Monthly registration trends (last 6 months)
    monthly_stats = []
    for i in range(6):
        month_start = (this_month - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        count = Registration.objects.filter(
            registration_date__gte=month_start,
            registration_date__lte=month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%B %Y'),
            'count': count
        })
    
    # Top performing modules
    top_modules = Module.objects.annotate(
        registration_count=Count('registrations')
    ).filter(registration_count__gt=0).order_by('-registration_count')[:5]
    
    context = {
        'total_students': total_students,
        'total_modules': total_modules,
        'total_registrations': total_registrations,
        'active_modules': active_modules,
        'recent_registrations': recent_registrations,
        'recent_students': recent_students,
        'module_stats': module_stats,
        'category_stats': category_stats,
        'status_stats': status_stats,
        'monthly_stats': monthly_stats,
        'top_modules': top_modules,
    }
    
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def bulk_operations(request):
    """Bulk operations interface for admin"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')
        
        if action == 'activate_modules':
            Module.objects.filter(id__in=selected_ids).update(availability=True)
            messages.success(request, f'{len(selected_ids)} modules activated successfully.')
        elif action == 'deactivate_modules':
            Module.objects.filter(id__in=selected_ids).update(availability=False)
            messages.success(request, f'{len(selected_ids)} modules deactivated successfully.')
        elif action == 'approve_registrations':
            Registration.objects.filter(id__in=selected_ids).update(status='A')
            messages.success(request, f'{len(selected_ids)} registrations approved successfully.')
        elif action == 'reject_registrations':
            Registration.objects.filter(id__in=selected_ids).update(status='R')
            messages.success(request, f'{len(selected_ids)} registrations rejected successfully.')
        
        return redirect('admin:bulk_operations')
    
    # Get data for bulk operations
    modules = Module.objects.all().order_by('code')
    registrations = Registration.objects.select_related('student__user', 'module').order_by('-registration_date')
    
    context = {
        'modules': modules,
        'registrations': registrations,
    }
    
    return render(request, 'admin/bulk_operations.html', context)

@staff_member_required
def csv_import(request):
    """CSV import interface for bulk data import"""
    
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        model_type = request.POST.get('model_type')
        
        if csv_file and model_type:
            try:
                # Process CSV file based on model type
                if model_type == 'modules':
                    success_count = import_modules_from_csv(csv_file)
                    messages.success(request, f'{success_count} modules imported successfully.')
                elif model_type == 'students':
                    success_count = import_students_from_csv(csv_file)
                    messages.success(request, f'{success_count} students imported successfully.')
                else:
                    messages.error(request, 'Invalid model type selected.')
                    
            except Exception as e:
                messages.error(request, f'Error importing CSV: {str(e)}')
        else:
            messages.error(request, 'Please select a file and model type.')
    
    context = {
        'model_types': [
            ('modules', 'Modules'),
            ('students', 'Students'),
        ]
    }
    
    return render(request, 'admin/csv_import.html', context)

def import_modules_from_csv(csv_file):
    """Import modules from CSV file"""
    decoded_file = csv_file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    success_count = 0
    for row in reader:
        try:
            Module.objects.create(
                name=row['name'],
                code=row['code'],
                credit=int(row['credit']),
                category=row['category'],
                description=row['description'],
                availability=row['availability'].lower() == 'true',
                courses_allowed=int(row['courses_allowed'])
            )
            success_count += 1
        except Exception as e:
            print(f"Error importing module {row.get('code', 'unknown')}: {e}")
    
    return success_count

def import_students_from_csv(csv_file):
    """Import students from CSV file"""
    decoded_file = csv_file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    
    success_count = 0
    for row in reader:
        try:
            # Create user first
            user = User.objects.create_user(
                username=row['username'],
                email=row['email'],
                password=row['password'],
                first_name=row['first_name'],
                last_name=row['last_name'],
                is_student=True
            )
            
            # Create student profile
            Student.objects.create(
                user=user,
                date_of_birth=datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date(),
                address=row.get('address', ''),
                city=row.get('city', ''),
                country=row.get('country', ''),
                phone=row.get('phone', '')
            )
            success_count += 1
        except Exception as e:
            print(f"Error importing student {row.get('username', 'unknown')}: {e}")
    
    return success_count

@staff_member_required
def audit_logs(request):
    """View admin audit logs"""
    
    logs = AdminAuditLog.objects.select_related('admin_user').order_by('-timestamp')
    
    # Filtering
    action_filter = request.GET.get('action')
    model_filter = request.GET.get('model')
    user_filter = request.GET.get('user')
    
    if action_filter:
        logs = logs.filter(action=action_filter)
    if model_filter:
        logs = logs.filter(model_name=model_filter)
    if user_filter:
        logs = logs.filter(admin_user__username__icontains=user_filter)
    
    # Pagination
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'actions': AdminAuditLog.ACTION_CHOICES,
        'models': AdminAuditLog.objects.values_list('model_name', flat=True).distinct(),
        'action_filter': action_filter,
        'model_filter': model_filter,
        'user_filter': user_filter,
    }
    
    return render(request, 'admin/audit_logs.html', context)

@staff_member_required
def reports(request):
    """Generate various reports"""
    
    report_type = request.GET.get('type', 'enrollment')
    
    if report_type == 'enrollment':
        # Enrollment report
        modules = Module.objects.annotate(
            student_count=Count('registrations'),
            male_count=Count('registrations__student', filter=Q(registrations__student__gender='M')),
            female_count=Count('registrations__student', filter=Q(registrations__student__gender='F'))
        ).order_by('-student_count')
        
        context = {
            'report_type': 'enrollment',
            'modules': modules,
            'total_students': Student.objects.count(),
            'total_registrations': Registration.objects.count(),
        }
        
    elif report_type == 'geographic':
        # Geographic distribution report
        city_stats = Student.objects.values('city').annotate(
            count=Count('id')
        ).order_by('-count')[:20]
        
        country_stats = Student.objects.values('country').annotate(
            count=Count('id')
        ).order_by('-count')
        
        context = {
            'report_type': 'geographic',
            'city_stats': city_stats,
            'country_stats': country_stats,
        }
        
    elif report_type == 'academic':
        # Academic performance report
        grade_stats = Registration.objects.exclude(grade__isnull=True).values('grade').annotate(
            count=Count('id')
        ).order_by('grade')
        
        module_performance = Module.objects.annotate(
            avg_grade=Avg('registrations__grade'),
            total_students=Count('registrations')
        ).filter(total_students__gt=0).order_by('-avg_grade')
        
        context = {
            'report_type': 'academic',
            'grade_stats': grade_stats,
            'module_performance': module_performance,
        }
    
    else:
        context = {'report_type': 'enrollment'}
    
    return render(request, 'admin/reports.html', context)

@staff_member_required
def api_dashboard(request):
    """API usage and management dashboard"""
    
    # Get API statistics
    total_api_calls = 0  # This would come from your API tracking system
    recent_api_calls = []  # This would come from your API tracking system
    
    context = {
        'total_api_calls': total_api_calls,
        'recent_api_calls': recent_api_calls,
    }
    
    return render(request, 'admin/api_dashboard.html', context)
