from django.urls import path
from . import views
from . import admin_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication
    path('register/', views.register_user, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', views.logout, name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    # Courses
    path('courses/', views.courses, name='courses'),
    path('courses/<str:course_code>/', views.course_detail, name='course_detail'),
    path('courses/<str:course_code>/enroll/', views.enroll_course, name='enroll_course'),
    
    # Modules
    path('modules/', views.modules, name='modules'),
    path('modules/<str:module_code>/', views.module_detail, name='module_detail'),
    path('modules/<str:module_code>/register/', views.register_module, name='register_module'),
    path('modules/<str:module_code>/unregister/', views.unregister_module, name='unregister_module'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('my-registrations/', views.my_registrations, name='my_registrations'),
    
    # API endpoints
    path('api/modules/', views.api_modules, name='api_modules'),
    path('api/external/', views.api_external_data, name='api_external'),
    
    # Admin-specific URLs
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/bulk-operations/', admin_views.bulk_operations, name='admin_bulk_operations'),
    path('admin/csv-import/', admin_views.csv_import, name='admin_csv_import'),
    path('admin/audit-logs/', admin_views.audit_logs, name='admin_audit_logs'),
    path('admin/reports/', admin_views.reports, name='admin_reports'),
    path('admin/api-dashboard/', admin_views.api_dashboard, name='admin_api_dashboard'),
] 