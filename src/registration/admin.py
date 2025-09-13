import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin  # type: ignore
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.http import HttpResponse
from django.utils import timezone
from django.utils.html import format_html
from django.contrib import messages
from .models import Course, Module, Student, Registration, PageContent, AdminAuditLog

User = get_user_model()

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'duration_years', 'total_credits', 'students_count', 'is_active']
    list_filter = ['category', 'is_active', 'duration_years', 'created_at']
    search_fields = ['code', 'name', 'description']
    list_editable = ['is_active', 'duration_years', 'total_credits']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['export_as_csv', 'bulk_activate', 'bulk_deactivate', 'create_course_groups']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'category', 'description')
        }),
        ('Program Details', {
            'fields': ('duration_years', 'total_credits')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='Course',
            object_id=str(obj.id),
            object_repr=f"{obj.code} - {obj.name}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'Course "{obj.name}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'Course "{obj.name}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def students_count(self, obj):
        count = obj.students.count()
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: gray;">{}</span>', count)
    students_count.short_description = 'Enrolled Students'
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=courses_export_{timezone.now().strftime("%Y%m%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Code', 'Name', 'Category', 'Duration (Years)', 'Total Credits', 'Description', 'Status'])
        
        for obj in queryset:
            writer.writerow([
                obj.code, obj.name, obj.get_category_display(), obj.duration_years,
                obj.total_credits, obj.description, 'Active' if obj.is_active else 'Inactive'
            ])
        return response
    export_as_csv.short_description = "Export selected courses to CSV"
    
    def bulk_activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} courses have been activated and are now available for enrollment.')
        
        # Log bulk action
        for course in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Course',
                object_id=str(course.id),
                object_repr=f"{course.code} - {course.name}",
                ip_address=self.get_client_ip(request)
            )
    bulk_activate.short_description = "Activate selected courses"
    
    def bulk_deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} courses have been deactivated and are no longer available for enrollment.')
        
        # Log bulk action
        for course in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Course',
                object_id=str(course.id),
                object_repr=f"{course.code} - {course.name}",
                ip_address=self.get_client_ip(request)
            )
    bulk_deactivate.short_description = "Deactivate selected courses"
    
    def create_course_groups(self, request, queryset):
        """Create Django Groups for selected courses"""
        created_count = 0
        for course in queryset:
            group = course.ensure_group_exists()
            if group:
                created_count += 1
        
        if created_count > 0:
            self.message_user(request, f'Django Groups created for {created_count} courses.')
        else:
            self.message_user(request, 'All course groups already exist.')
    create_course_groups.short_description = "Create Django Groups for selected courses"

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'category', 'credit', 'availability', 'courses_linked', 'registered_students_count', 'available_slots']
    list_filter = ['category', 'availability', 'created_at', 'credit', 'courses']
    search_fields = ['code', 'name', 'description']
    list_editable = ['availability']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['courses']
    actions = ['export_as_csv', 'bulk_activate', 'bulk_deactivate', 'export_registrations', 'send_notifications']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'category', 'credit', 'description')
        }),
        ('Availability', {
            'fields': ('availability', 'courses_allowed')
        }),
        ('Course Links', {
            'fields': ('courses',),
            'description': 'Select which courses this module is available for'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='Module',
            object_id=str(obj.id),
            object_repr=f"{obj.code} - {obj.name}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'Module "{obj.name}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'Module "{obj.name}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def courses_linked(self, obj):
        """Display linked courses"""
        courses = obj.courses.all()
        if courses:
            return ', '.join([course.code for course in courses])
        return 'All Courses'
    courses_linked.short_description = 'Linked Courses'
    
    def registered_students_count(self, obj):
        count = obj.registrations.count()
        if count > 0:
            return format_html('<span style="color: green;">{}</span>', count)
        return format_html('<span style="color: gray;">{}</span>', count)
    registered_students_count.short_description = 'Registered Students'
    
    def available_slots(self, obj):
        available = obj.courses_allowed - obj.registrations.count()
        if available > 0:
            return format_html('<span style="color: green;">{}</span>', available)
        return format_html('<span style="color: red;">{}</span>', available)
    available_slots.short_description = 'Available Slots'
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=modules_export_{timezone.now().strftime("%Y%m%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Code', 'Name', 'Category', 'Credit', 'Description', 'Availability', 'Courses Allowed', 'Linked Courses'])
        
        for obj in queryset:
            linked_courses = ', '.join([course.code for course in obj.courses.all()]) if obj.courses.exists() else 'All'
            writer.writerow([
                obj.code, obj.name, obj.get_category_display(), obj.credit,
                obj.description, 'Open' if obj.availability else 'Closed',
                obj.courses_allowed, linked_courses
            ])
        return response
    export_as_csv.short_description = "Export selected modules to CSV"
    
    def bulk_activate(self, request, queryset):
        updated = queryset.update(availability=True)
        self.message_user(request, f'{updated} modules have been activated.')
        
        # Log bulk action
        for module in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Module',
                object_id=str(module.id),
                object_repr=f"{module.code} - {module.name}",
                ip_address=self.get_client_ip(request)
            )
    bulk_activate.short_description = "Activate selected modules"
    
    def bulk_deactivate(self, request, queryset):
        updated = queryset.update(availability=False)
        self.message_user(request, f'{updated} modules have been deactivated.')
        
        # Log bulk action
        for module in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Module',
                object_id=str(module.id),
                object_repr=f"{module.code} - {module.name}",
                ip_address=self.get_client_ip(request)
            )
    bulk_deactivate.short_description = "Deactivate selected modules"
    
    def export_registrations(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=module_registrations_{timezone.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)
        writer.writerow([
            'Module Code', 'Module Name', 'Student ID', 'Student Name', 'Email',
            'Status', 'Grade', 'Registration Date', 'Notes'
        ])
        for module in queryset:
            for registration in module.registrations.select_related('student__user'):
                writer.writerow([
                    module.code, module.name, registration.student.student_id,
                    registration.student.user.get_full_name(), registration.student.user.email,
                    registration.get_status_display(), registration.grade or '',
                    registration.registration_date.strftime('%Y-%m-%d %H:%M'),
                    registration.notes or ''
                ])
        return response
    export_registrations.short_description = "Export detailed registrations"
    
    def send_notifications(self, request, queryset):
        # Placeholder for notification functionality
        self.message_user(request, f'Notifications would be sent for {queryset.count()} modules.')
    send_notifications.short_description = "Send notifications to registered students"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'user_full_name', 'email', 'course', 'city', 'country', 'registration_count', 'is_active']
    list_filter = ['course', 'city', 'country', 'is_active', 'created_at', 'gender', 'enrollment_date']
    search_fields = ['student_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'course__name']
    ordering = ['student_id']
    readonly_fields = ['student_id', 'created_at', 'updated_at']
    actions = ['export_as_csv', 'bulk_activate', 'bulk_deactivate', 'export_academic_history', 'send_welcome_email']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'student_id')
        }),
        ('Course Information', {
            'fields': ('course', 'enrollment_date', 'expected_graduation')
        }),
        ('Personal Information', {
            'fields': ('date_of_birth', 'gender', 'photo', 'bio')
        }),
        ('Contact Information', {
            'fields': ('address', 'city', 'state', 'postal_code', 'country', 'phone')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact', 'emergency_phone'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='Student',
            object_id=str(obj.id),
            object_repr=f"{obj.student_id} - {obj.user.get_full_name()}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'Student "{obj.user.get_full_name()}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'Student "{obj.user.get_full_name()}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def user_full_name(self, obj):
        return obj.user.get_full_name()
    user_full_name.short_description = 'Name'
    user_full_name.admin_order_field = 'user__last_name'
    
    def email(self, obj):
        return obj.user.email
    email.short_description = 'Email'
    
    def registration_count(self, obj):
        count = obj.registrations.count()
        if count > 0:
            return format_html('<span style="color: blue;">{}</span>', count)
        return format_html('<span style="color: gray;">{}</span>', count)
    registration_count.short_description = 'Registrations'
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=students_export_{timezone.now().strftime("%Y%m%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Username', 'First Name', 'Last Name', 'Email', 'Course', 'City', 'Country', 'Phone', 'Enrollment Date'])
        
        for obj in queryset:
            writer.writerow([
                obj.student_id, obj.user.username, obj.user.first_name, obj.user.last_name,
                obj.user.email, obj.course.name if obj.course else '', obj.city, obj.country, 
                obj.phone or '', obj.enrollment_date.strftime('%Y-%m-%d') if obj.enrollment_date else ''
            ])
        return response
    export_as_csv.short_description = "Export selected students to CSV"
    
    def bulk_activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} students have been activated.')
        
        # Log bulk action
        for student in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Student',
                object_id=str(student.id),
                object_repr=f"{student.student_id} - {student.user.get_full_name()}",
                ip_address=self.get_client_ip(request)
            )
    bulk_activate.short_description = "Activate selected students"
    
    def bulk_deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} students have been deactivated.')
        
        # Log bulk action
        for student in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Student',
                object_id=str(student.id),
                object_repr=f"{student.student_id} - {student.user.get_full_name()}",
                ip_address=self.get_client_ip(request)
            )
    bulk_deactivate.short_description = "Deactivate selected students"
    
    def export_academic_history(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=academic_history_{timezone.now().strftime("%Y%m%d")}.csv'
        writer = csv.writer(response)
        writer.writerow([
            'Student ID', 'Student Name', 'Course', 'Total Credits', 'Modules Registered', 'Status'
        ])
        for student in queryset:
            total_credits = student.get_total_credits()
            modules_count = student.registrations.count()
            writer.writerow([
                student.student_id, student.user.get_full_name(), 
                student.course.name if student.course else '', total_credits, modules_count,
                'Active' if student.is_active else 'Inactive'
            ])
        return response
    export_academic_history.short_description = "Export academic history"
    
    def send_welcome_email(self, request, queryset):
        # Placeholder for welcome email functionality
        self.message_user(request, f'Welcome emails would be sent to {queryset.count()} students.')
    send_welcome_email.short_description = "Send welcome emails"

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['student', 'module', 'status', 'grade', 'registration_date', 'status_color']
    list_filter = ['status', 'module__category', 'registration_date']
    search_fields = ['student__user__username', 'student__user__first_name', 'student__user__last_name', 'module__code', 'module__name']
    date_hierarchy = 'registration_date'
    list_editable = ['status', 'grade']
    actions = ['export_as_csv', 'bulk_approve', 'bulk_reject']
    readonly_fields = ['registration_date', 'last_modified']
    
    fieldsets = (
        ('Registration Details', {
            'fields': ('student', 'module', 'status', 'grade')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('registration_date', 'last_modified'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='Registration',
            object_id=str(obj.id),
            object_repr=f"{obj.student.student_id} - {obj.module.code}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'Registration for "{obj.student.user.get_full_name()}" on "{obj.module.name}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'Registration for "{obj.student.user.get_full_name()}" on "{obj.module.name}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def status_color(self, obj):
        colors = {
            'P': 'orange',
            'A': 'green', 
            'R': 'red',
            'W': 'purple',
            'D': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_color.short_description = 'Status'
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=registrations_export_{timezone.now().strftime("%Y%m%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Student ID', 'Student Name', 'Module Code', 'Module Name', 'Status', 'Grade', 'Registration Date'])
        
        for registration in queryset.select_related('student__user', 'module'):
            writer.writerow([
                registration.student.student_id,
                registration.student.user.get_full_name(),
                registration.module.code,
                registration.module.name,
                registration.get_status_display(),
                registration.grade or '',
                registration.registration_date.strftime('%Y-%m-%d %H:%M')
            ])
        return response
    export_as_csv.short_description = "Export selected registrations to CSV"
    
    def bulk_approve(self, request, queryset):
        updated = queryset.update(status='A')
        self.message_user(request, f'{updated} registrations have been approved.')
        
        # Log bulk action
        for registration in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Registration',
                object_id=str(registration.id),
                object_repr=f"{registration.student.student_id} - {registration.module.code}",
                ip_address=self.get_client_ip(request)
            )
    bulk_approve.short_description = "Approve selected registrations"
    
    def bulk_reject(self, request, queryset):
        updated = queryset.update(status='R')
        self.message_user(request, f'{updated} registrations have been rejected.')
        
        # Log bulk action
        for registration in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='Registration',
                object_id=str(registration.id),
                object_repr=f"{registration.student.student_id} - {registration.module.code}",
                ip_address=self.get_client_ip(request)
            )
    bulk_reject.short_description = "Reject selected registrations"

# Custom Group Admin for better management
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'user_count', 'permission_count']
    search_fields = ['name']
    filter_horizontal = ['permissions']
    ordering = ['name']
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='Group',
            object_id=str(obj.id),
            object_repr=f"{obj.name}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'Group "{obj.name}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'Group "{obj.name}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def user_count(self, obj):
        return obj.user_set.count()
    user_count.short_description = 'Users'
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'

# Register the custom Group admin (unregister default first)
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

# Enhanced User Admin
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_student', 'is_teacher', 'date_joined')
    list_filter = ('is_staff', 'is_student', 'is_teacher', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    actions = ['export_as_csv', 'bulk_activate', 'bulk_deactivate']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email', 'phone_number')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Custom Fields', {
            'fields': ('is_student', 'is_teacher')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'password1', 'password2', 
                'is_staff', 'is_student', 'is_teacher'
            ),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='User',
            object_id=str(obj.id),
            object_repr=f"{obj.username} - {obj.email}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'User "{obj.username}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'User "{obj.username}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=users_export_{timezone.now().strftime("%Y%m%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'First Name', 'Last Name', 'Is Staff', 'Is Student', 'Is Teacher', 'Date Joined'])
        
        for obj in queryset:
            writer.writerow([
                obj.username, obj.email, obj.first_name, obj.last_name,
                obj.is_staff, obj.is_student, obj.is_teacher,
                obj.date_joined.strftime('%Y-%m-%d %H:%M')
            ])
        return response
    export_as_csv.short_description = "Export selected users to CSV"
    
    def bulk_activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users have been activated.')
        
        # Log bulk action
        for user in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='User',
                object_id=str(user.id),
                object_repr=f"{user.username} - {user.email}",
                ip_address=self.get_client_ip(request)
            )
    bulk_activate.short_description = "Activate selected users"
    
    def bulk_deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users have been deactivated.')
        
        # Log bulk action
        for user in queryset:
            AdminAuditLog.objects.create(
                admin_user=request.user,
                action='UPDATE',
                model_name='User',
                object_id=str(user.id),
                object_repr=f"{user.username} - {user.email}",
                ip_address=self.get_client_ip(request)
            )
    bulk_deactivate.short_description = "Deactivate selected users"

# Enhanced PageContent Admin
@admin.register(PageContent)
class PageContentAdmin(admin.ModelAdmin):
    list_display = ['page', 'title', 'last_updated', 'content_preview']
    list_filter = ['page', 'last_updated']
    search_fields = ['title', 'content']
    readonly_fields = ['last_updated']
    actions = ['export_content']
    
    fieldsets = (
        ('Page Information', {
            'fields': ('page', 'title')
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('last_updated',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Override save to ensure immediate effect and log changes"""
        super().save_model(request, obj, form, change)
        
        # Log the admin action
        action = 'UPDATE' if change else 'CREATE'
        AdminAuditLog.objects.create(
            admin_user=request.user,
            action=action,
            model_name='PageContent',
            object_id=str(obj.id),
            object_repr=f"{obj.page} - {obj.title}",
            ip_address=self.get_client_ip(request)
        )
        
        # Show immediate effect message
        if change:
            messages.success(request, f'Page content for "{obj.page}" has been updated successfully. Changes are now active.')
        else:
            messages.success(request, f'Page content for "{obj.page}" has been created successfully.')
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def content_preview(self, obj):
        """Show a preview of the content"""
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def export_content(self, request, queryset):
        """Export page content to CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=page_content_{timezone.now().strftime("%Y%m%d")}.csv'
        
        writer = csv.writer(response)
        writer.writerow(['Page', 'Title', 'Content', 'Last Updated'])
        
        for obj in queryset:
            writer.writerow([
                obj.get_page_display(), obj.title, obj.content, 
                obj.last_updated.strftime('%Y-%m-%d %H:%M')
            ])
        return response
    export_content.short_description = "Export content to CSV"

# AdminAuditLog Admin
@admin.register(AdminAuditLog)
class AdminAuditLogAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'action', 'model_name', 'object_repr', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['admin_user__username', 'object_repr']
    readonly_fields = ['admin_user', 'action', 'model_name', 'object_id', 'object_repr', 'timestamp', 'ip_address']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

admin.site.register(User, UserAdmin)

# Set admin site headers
admin.site.site_header = 'University Registration System Admin'
admin.site.site_title = 'University Registration System'
admin.site.index_title = 'Welcome to the University Registration System'

# Custom Admin Index to show recent changes
class CustomAdminSite(admin.AdminSite):
    site_header = 'University Registration System Admin'
    site_title = 'University Registration System'
    index_title = 'Welcome to the University Registration System - Changes Take Effect Immediately'
    
    def index(self, request, extra_context=None):
        """Custom admin index with recent changes"""
        extra_context = extra_context or {}
        
        # Get recent admin actions
        recent_actions = AdminAuditLog.objects.select_related('admin_user').order_by('-timestamp')[:10]
        
        # Get system statistics
        stats = {
            'total_students': Student.objects.count(),
            'total_courses': Course.objects.filter(is_active=True).count(),
            'total_modules': Module.objects.filter(availability=True).count(),
            'total_registrations': Registration.objects.filter(status='A').count(),
            'pending_registrations': Registration.objects.filter(status='P').count(),
        }
        
        extra_context.update({
            'recent_actions': recent_actions,
            'stats': stats,
            'show_recent_changes': True,
        })
        
        return super().index(request, extra_context)

# Replace the default admin site with our custom one
admin_site = CustomAdminSite(name='custom_admin')

# Re-register all models with the custom admin site
admin_site.register(Course, CourseAdmin)
admin_site.register(Module, ModuleAdmin)
admin_site.register(Student, StudentAdmin)
admin_site.register(Registration, RegistrationAdmin)
admin_site.register(PageContent, PageContentAdmin)
admin_site.register(AdminAuditLog, AdminAuditLogAdmin)
admin_site.register(User, UserAdmin)
admin_site.register(Group, CustomGroupAdmin)

# Custom admin site is now ready with immediate effect features
