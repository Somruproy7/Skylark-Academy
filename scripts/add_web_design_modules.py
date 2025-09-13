#!/usr/bin/env python
"""
Script to add Web Design modules for Arts students
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from registration.models import Module, Course

def add_web_design_modules():
    """Add Web Design modules that Arts students can register for"""
    
    # Check if Web Design modules already exist
    existing_modules = Module.objects.filter(name__icontains='Web Design')
    if existing_modules.exists():
        print(f"Found {existing_modules.count()} existing Web Design modules:")
        for module in existing_modules:
            print(f"  - {module.code}: {module.name} (Category: {module.category})")
        return
    
    # Create Web Design modules
    web_design_modules = [
        {
            'code': 'WD101',
            'name': 'Introduction to Web Design',
            'category': 'CS',
            'credit': 3,
            'description': 'Learn the fundamentals of web design including HTML, CSS, and basic design principles.',
            'availability': True,
            'courses_allowed': 30
        },
        {
            'code': 'WD201',
            'name': 'Advanced Web Design',
            'category': 'CS',
            'credit': 4,
            'description': 'Advanced web design techniques including responsive design, JavaScript, and modern frameworks.',
            'availability': True,
            'courses_allowed': 25
        },
        {
            'code': 'WD301',
            'name': 'Web Design Portfolio',
            'category': 'ART',
            'credit': 3,
            'description': 'Create a professional web design portfolio showcasing your skills and projects.',
            'availability': True,
            'courses_allowed': 20
        }
    ]
    
    created_modules = []
    for module_data in web_design_modules:
        module, created = Module.objects.get_or_create(
            code=module_data['code'],
            defaults=module_data
        )
        if created:
            created_modules.append(module)
            print(f"Created module: {module.code} - {module.name}")
        else:
            print(f"Module already exists: {module.code} - {module.name}")
    
    if created_modules:
        print(f"\nSuccessfully created {len(created_modules)} Web Design modules!")
        print("Arts students should now be able to register for these modules.")
    else:
        print("\nAll Web Design modules already exist.")

if __name__ == '__main__':
    add_web_design_modules()
