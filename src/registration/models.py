from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Custom User Model
class User(AbstractUser):
    is_student = models.BooleanField(
        'student status',
        default=models.NOT_PROVIDED,
        help_text='Designates whether the user is a student.'
    )
    is_teacher = models.BooleanField(
        'teacher status',
        default=models.NOT_PROVIDED,
        help_text='Designates whether the user is a teacher.'
    )
    phone_number = models.CharField(
        'phone number',
        max_length=20,
        blank=True,
        null=True,
        help_text='User\'s phone number.'
    )
    date_joined = models.DateTimeField(
        'date joined',
        default=timezone.now,
        help_text='When the user account was created.'
    )
    
    class Meta:
        db_table = 'registration_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.get_full_name() or self.username

# Course Model - Each student belongs to only one course
class Course(models.Model):
    objects = models.Manager()
    COURSE_CHOICES = [
        ('CS', 'Computer Science'),
        ('MATH', 'Mathematics'),
        ('ENG', 'Engineering'),
        ('BUS', 'Business'),
        ('ART', 'Arts'),
        ('MED', 'Medicine'),
        ('LAW', 'Law'),
        ('EDU', 'Education'),
        ('SCI', 'Science'),
        ('HUM', 'Humanities'),
    ]
    
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=10, choices=COURSE_CHOICES)
    description = models.TextField()
    duration_years = models.IntegerField(
        default=3, 
        validators=[MinValueValidator(1), MaxValueValidator(6)]
    )
    total_credits = models.IntegerField(
        default=120, 
        validators=[MinValueValidator(60), MaxValueValidator(600)]
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['code']
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    def get_students_count(self) -> int:
        """Get the number of students enrolled in this course"""
        # Using the related_name 'students' from the Student model's course field
        return getattr(self, 'students', self.__class__.objects.none()).count()
    get_students_count.short_description = 'Enrolled Students'
    
    def get_group_name(self) -> str:
        """Get the Django Group name for this course"""
        return f"Course_{self.code}"
    
    def ensure_group_exists(self) -> Group:
        """Ensure the Django Group for this course exists"""
        group_name = self.get_group_name()
        group, _ = Group.objects.get_or_create(name=group_name)
        return group

class Module(models.Model):
    objects = models.Manager()
    
    CATEGORY_CHOICES = [
        ('CS', 'Computer Science'),
        ('MATH', 'Mathematics'),
        ('ENG', 'Engineering'),
        ('BUS', 'Business'),
        ('ART', 'Arts'),
    ]
    
    name = models.CharField('name', max_length=200)
    code = models.CharField('code', max_length=20, unique=True)
    credit = models.IntegerField(
        'credit',
        validators=[MinValueValidator(1), MaxValueValidator(30)]
    )
    category = models.CharField('category', max_length=10, choices=CATEGORY_CHOICES)
    description = models.TextField('description')
    availability = models.BooleanField('availability', default=True)
    courses_allowed = models.IntegerField('courses allowed', default=30)
    # Link module to specific courses
    courses = models.ManyToManyField(
        Course,
        related_name='modules',
        blank=True,
        verbose_name='courses'
    )
    created_at = models.DateTimeField('created at', auto_now_add=True)
    updated_at = models.DateTimeField('updated at', auto_now=True)
    
    # Type hints for reverse relations
    if TYPE_CHECKING:
        registrations: 'models.Manager'  # type: ignore
    
    def __str__(self):
        return f"{self.code} - {self.name}"
        
    def registered_students_count(self) -> int:
        return self.registrations.count()
    registered_students_count.short_description = 'Registered Students'
    
    def available_slots(self) -> int:
        return max(0, self.courses_allowed - self.registrations.count())
    available_slots.short_description = 'Available Slots'
    
    class Meta:
        ordering = ['code']

class Student(models.Model):
    objects = models.Manager()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('U', 'Prefer not to say')
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile'
    )
    student_id = models.CharField(
        'student ID',
        max_length=20,
        unique=True,
        help_text='Student identification number.'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text='The course the student is enrolled in.'
    )
    date_of_birth = models.DateField(
        'date of birth',
        null=True,
        blank=True
    )
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    address = models.TextField(
        'address',
        blank=True,
        null=True
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, blank=True, null=True)
    emergency_phone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='student_photos/%Y/%m/%d/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    enrollment_date = models.DateField(default=timezone.now)
    expected_graduation = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = 'Student'
        verbose_name_plural = 'Students'
    
    def __str__(self):
        user = getattr(self, 'user', None)
        if user is not None and hasattr(user, 'get_full_name'):
            return f"{user.get_full_name()} ({self.student_id})"
        return f"Student ({self.student_id})"
    
    def save(self, *args, **kwargs):
        """Override save to automatically add user to course group"""
        super().save(*args, **kwargs)
        # Only proceed if course is set
        if hasattr(self, 'course') and self.course is not None:
            # Get the course instance
            course = self.course
            # Create group name based on course code or ID
            course_code = getattr(course, 'code', None)
            if course_code is None:
                # If course has no code attribute, use its string representation
                course_code = str(course) if course else 'unknown'
            group_name = f"Course_{course_code}_Group"
            group, _ = Group.objects.get_or_create(name=group_name)
            # Add user to the course group
            user = getattr(self, 'user', None)
            if user is not None and hasattr(user, 'groups'):
                user.groups.add(group)
    
    def get_course_group(self) -> Optional[Group]:
        """Get the Django Group for this student's course"""
        if not hasattr(self, 'course') or not self.course:
            return None
            
        course = self.course
        course_code = getattr(course, 'code', None)
        if course_code is None:
            # If course has no code attribute, use its string representation
            course_code = str(course) if course else 'unknown'
        group_name = f"Course_{course_code}_Group"
        group, _ = Group.objects.get_or_create(name=group_name)
        return group
    
    def get_enrolled_modules(self):
        """Get all modules the student is registered for"""
        from .models import Module, Registration
        return Module.objects.filter(
            id__in=Registration.objects.filter(
                student_id=self.pk,
                status='A'
            ).values_list('module_id', flat=True)
        )

    def get_total_credits(self) -> int:
        """Get total credits earned by the student"""
        from django.db.models import Sum
        from .models import Registration
        
        result = Registration.objects.filter(
            student_id=self.pk,
            status='A'
        ).aggregate(
            total=Sum('module__credit')
        )
        return int(result['total']) if result['total'] is not None else 0

class Registration(models.Model):
    objects = models.Manager()
    STATUS_CHOICES = [
        ('P', 'Pending'),
        ('A', 'Approved'),
        ('R', 'Rejected'),
        ('W', 'Waitlisted'),
        ('D', 'Dropped')
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='registrations')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='registrations')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    grade = models.CharField(max_length=2, blank=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'module')
        ordering = ['-registration_date']
        verbose_name = 'Module Registration'
        verbose_name_plural = 'Module Registrations'
    
    def __str__(self):
        return f"{self.student} - {self.module}"
    
    def get_status_display(self):
        """Get the display name for the status"""
        return dict(self.STATUS_CHOICES).get(self.status, self.status)

# Content Management Model for static pages
class PageContent(models.Model):
    objects = models.Manager()
    PAGE_CHOICES = [
        ('home', 'Home Page'),
        ('about', 'About Us'),
        ('contact', 'Contact Us'),
        ('modules_list', 'Modules List'),
    ]
    
    page = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Page Content'
        verbose_name_plural = 'Page Contents'
    
    def get_page_display(self) -> str:
        """Get the display name for the page."""
        page_value = self.page if isinstance(self.page, str) else str(self.page)
        return dict(self.PAGE_CHOICES).get(page_value, page_value)
    
    def __str__(self) -> str:
        return f"{self.get_page_display()} - {self.title}"

# Audit Log Model for tracking admin actions
class AdminAuditLog(models.Model):
    objects = models.Manager()
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('VIEW', 'View'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50)
    object_id = models.CharField(max_length=50)
    object_repr = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Admin Audit Log'
        verbose_name_plural = 'Admin Audit Logs'
    
    def __str__(self):
        return f"{self.admin_user} - {self.action} {self.model_name} at {self.timestamp}"
