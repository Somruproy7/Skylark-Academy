from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import Group
from django.utils import timezone
from .models import Course, Module, Student, Registration, AdminAuditLog

# Import models safely to avoid circular imports
def get_models():
    try:
        from .models import AdminAuditLog, User
        return AdminAuditLog, User
    except ImportError:
        return None, None

# Signal handlers will be registered when models are available
def register_signals():
    AdminAuditLog, User = get_models()
    if AdminAuditLog and User:
        @receiver(post_save, sender=User)
        def log_user_changes(sender, instance, created, **kwargs):
            """Log user model changes"""
            if hasattr(instance, '_current_user'):  # Check if this is an admin action
                AdminAuditLog.objects.create(
                    admin_user=instance._current_user,
                    action='CREATE' if created else 'UPDATE',
                    model_name='User',
                    object_id=str(instance.id),
                    object_repr=f"{instance.username} ({instance.get_full_name()})",
                    ip_address=getattr(instance._current_user, '_ip_address', None)
                )

        @receiver(post_delete, sender=User)
        def log_user_deletion(sender, instance, **kwargs):
            """Log user deletions"""
            if hasattr(instance, '_current_user'):
                AdminAuditLog.objects.create(
                    admin_user=instance._current_user,
                    action='DELETE',
                    model_name='User',
                    object_id=str(instance.id),
                    object_repr=f"{instance.username} ({instance.get_full_name()})",
                    ip_address=getattr(instance._current_user, '_ip_address', None)
                )

# Register signals when the function is called
register_signals()

@receiver(post_save, sender=Course)
def course_post_save(sender, instance, created, **kwargs):
    """Signal to handle course changes and ensure immediate effect"""
    if created:
        # Create course group when new course is created
        instance.ensure_group_exists()
    else:
        # Update course group when course is modified
        instance.ensure_group_exists()

@receiver(post_save, sender=Module)
def module_post_save(sender, instance, created, **kwargs):
    """Signal to handle module changes and ensure immediate effect"""
    # Any additional module-specific logic can be added here
    pass

@receiver(post_save, sender=Student)
def student_post_save(sender, instance, created, **kwargs):
    """Signal to handle student changes and ensure immediate effect"""
    if instance.course:
        # Ensure student is added to course group
        course_group = instance.course.ensure_group_exists()
        if course_group and instance.user:
            instance.user.groups.add(course_group)

@receiver(post_save, sender=Registration)
def registration_post_save(sender, instance, created, **kwargs):
    """Signal to handle registration changes and ensure immediate effect"""
    # Any additional registration-specific logic can be added here
    pass

@receiver(post_delete, sender=Course)
def course_post_delete(sender, instance, **kwargs):
    """Signal to handle course deletion"""
    # Clean up course group when course is deleted
    try:
        group_name = instance.get_group_name()
        group = Group.objects.get(name=group_name)
        group.delete()
    except Group.DoesNotExist:
        pass

@receiver(post_delete, sender=Student)
def student_post_delete(sender, instance, **kwargs):
    """Signal to handle student deletion"""
    # Remove student from course group when student is deleted
    if instance.course and instance.user:
        try:
            group_name = instance.course.get_group_name()
            group = Group.objects.get(name=group_name)
            instance.user.groups.remove(group)
        except Group.DoesNotExist:
            pass

# Admin action logging signal
@receiver(post_save, sender=AdminAuditLog)
def admin_audit_log_post_save(sender, instance, created, **kwargs):
    """Signal to handle admin audit log entries"""
    if created:
        # Log the admin action for tracking
        print(f"Admin Action Logged: {instance.admin_user} {instance.action} {instance.model_name} - {instance.object_repr}")
