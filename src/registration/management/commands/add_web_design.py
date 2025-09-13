from django.core.management.base import BaseCommand
from registration.models import Module, Course

class Command(BaseCommand):
    help = 'Add Web Design modules for Arts students'

    def handle(self, *args, **options):
        self.stdout.write("Adding Web Design modules...")
        
        # Create Web Design modules
        modules_data = [
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
        
        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                code=module_data['code'],
                defaults=module_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created module: {module.code} - {module.name}')
                )
            else:
                # Update existing module
                module.availability = True
                module.courses_allowed = module_data['courses_allowed']
                module.save()
                self.stdout.write(
                    self.style.WARNING(f'Updated module: {module.code} - {module.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully added/updated Web Design modules!')
        )
