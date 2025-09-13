#!/usr/bin/env python
"""
Setup script to create default admin user for University Registration System
Run this script after setting up the database and running migrations
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registrationApp.settings')

# Setup Django
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

def create_default_admin():
    """Create default admin user if it doesn't exist"""
    
    # Check if admin user already exists
    if User.objects.filter(username='admin').exists():
        print("✅ Admin user already exists!")
        admin_user = User.objects.get(username='admin')
        print(f"   Username: {admin_user.username}")
        print(f"   Email: {admin_user.email}")
        print(f"   Is Staff: {admin_user.is_staff}")
        print(f"   Is Superuser: {admin_user.is_superuser}")
        return
    
    try:
        # Create admin user
        admin_user = User.objects.create_user(
            username='admin',
            email='admin@university.edu',
            password='admin123',
            first_name='System',
            last_name='Administrator',
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        
        print("✅ Default admin user created successfully!")
        print(f"   Username: {admin_user.username}")
        print(f"   Password: admin123")
        print(f"   Email: {admin_user.email}")
        print(f"   Access URL: http://127.0.0.1:8000/admin/")
        
        # Create basic groups
        create_basic_groups()
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    
    return True

def create_basic_groups():
    """Create basic user groups"""
    
    groups_data = [
        'Students',
        'Teachers', 
        'Administrators',
        'Course_CS',
        'Course_MATH',
        'Course_ENG',
        'Course_BUS',
        'Course_ART'
    ]
    
    created_groups = []
    for group_name in groups_data:
        _, created = Group.objects.get_or_create(name=group_name)
        if created:
            created_groups.append(group_name)
    
    if created_groups:
        print(f"✅ Created groups: {', '.join(created_groups)}")
    else:
        print("✅ All groups already exist")

def create_sample_data():
    """Create sample courses and modules for testing"""
    
    # Add parent directory to Python path to find the registration app
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.append(parent_dir)
    from src.registration.models import Course, Module
    
    # Create sample courses
    courses_data = [
        {
            'name': 'Computer Science',
            'code': 'CS',
            'category': 'CS',
            'description': 'Bachelor of Science in Computer Science',
            'duration_years': 4,
            'total_credits': 480
        },
        {
            'name': 'Mathematics',
            'code': 'MATH',
            'category': 'MATH', 
            'description': 'Bachelor of Science in Mathematics',
            'duration_years': 3,
            'total_credits': 360
        },
        {
            'name': 'Engineering',
            'code': 'ENG',
            'category': 'ENG',
            'description': 'Bachelor of Engineering',
            'duration_years': 4,
            'total_credits': 480
        }
    ]
    
    created_courses = []
    for course_data in courses_data:
        course, created = Course.objects.get_or_create(
            code=course_data['code'],
            defaults=course_data
        )
        if created:
            created_courses.append(course.code)
    
    if created_courses:
        print(f"✅ Created sample courses: {', '.join(created_courses)}")
    
    # Create sample modules
    modules_data = [
        {
            'name': 'Introduction to Programming',
            'code': 'CS101',
            'category': 'CS',
            'credit': 15,
            'description': 'Basic programming concepts and Python',
            'courses_allowed': 50
        },
        {
            'name': 'Calculus I',
            'code': 'MATH101',
            'category': 'MATH',
            'credit': 20,
            'description': 'Fundamental calculus concepts',
            'courses_allowed': 40
        },
        {
            'name': 'Engineering Design',
            'code': 'ENG101',
            'category': 'ENG',
            'credit': 25,
            'description': 'Engineering design principles',
            'courses_allowed': 35
        }
    ]
    
    created_modules = []
    for module_data in modules_data:
        module, created = Module.objects.get_or_create(
            code=module_data['code'],
            defaults=module_data
        )
        if created:
            created_modules.append(module.code)
    
    if created_modules:
        print(f"✅ Created sample modules: {', '.join(created_modules)}")

def main():
    """Main setup function"""
    
    print("🚀 Setting up University Registration System...")
    print("=" * 50)
    
    # Create admin user
    if create_default_admin():
        print("\n📚 Creating sample data...")
        create_sample_data()
        
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the server: python manage.py runserver")
        print("2. Access admin panel: http://127.0.0.1:8000/admin/")
        print("3. Login with: admin / admin123")
        print("4. Access main site: http://127.0.0.1:8000/")
        
    else:
        print("\n❌ Setup failed. Please check the error messages above.")

if __name__ == '__main__':
    main()
