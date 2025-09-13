from django.core.management.base import BaseCommand
from registration.models import Module
from datetime import date

class Command(BaseCommand):
    help = 'Populate database with sample modules'

    def handle(self, *args, **options):
        # Sample modules data
        modules_data = [
            {
                'name': 'Introduction to Computer Science',
                'code': 'CS101',
                'credit': 3,
                'category': 'CS',
                'description': 'Fundamental concepts of computer science including algorithms, data structures, and programming principles.',
                'availability': True,
                'courses_allowed': 50
            },
            {
                'name': 'Advanced Programming',
                'code': 'CS201',
                'credit': 4,
                'category': 'CS',
                'description': 'Advanced programming concepts including object-oriented programming, design patterns, and software engineering.',
                'availability': True,
                'courses_allowed': 40
            },
            {
                'name': 'Database Systems',
                'code': 'CS301',
                'credit': 3,
                'category': 'CS',
                'description': 'Database design, SQL, and database management systems.',
                'availability': True,
                'courses_allowed': 35
            },
            {
                'name': 'Calculus I',
                'code': 'MATH101',
                'credit': 4,
                'category': 'MATH',
                'description': 'Introduction to calculus including limits, derivatives, and applications.',
                'availability': True,
                'courses_allowed': 60
            },
            {
                'name': 'Linear Algebra',
                'code': 'MATH201',
                'credit': 3,
                'category': 'MATH',
                'description': 'Vector spaces, linear transformations, and matrix operations.',
                'availability': True,
                'courses_allowed': 45
            },
            {
                'name': 'Statistics',
                'code': 'MATH301',
                'credit': 3,
                'category': 'MATH',
                'description': 'Probability theory, statistical inference, and data analysis.',
                'availability': True,
                'courses_allowed': 50
            },
            {
                'name': 'Mechanical Engineering Fundamentals',
                'code': 'ENG101',
                'credit': 4,
                'category': 'ENG',
                'description': 'Basic principles of mechanical engineering including mechanics and thermodynamics.',
                'availability': True,
                'courses_allowed': 40
            },
            {
                'name': 'Electrical Circuits',
                'code': 'ENG201',
                'credit': 3,
                'category': 'ENG',
                'description': 'Analysis of electrical circuits, components, and systems.',
                'availability': True,
                'courses_allowed': 35
            },
            {
                'name': 'Business Management',
                'code': 'BUS101',
                'credit': 3,
                'category': 'BUS',
                'description': 'Principles of business management, organizational behavior, and leadership.',
                'availability': True,
                'courses_allowed': 55
            },
            {
                'name': 'Financial Accounting',
                'code': 'BUS201',
                'credit': 3,
                'category': 'BUS',
                'description': 'Financial accounting principles, statements, and analysis.',
                'availability': True,
                'courses_allowed': 45
            },
            {
                'name': 'Marketing Principles',
                'code': 'BUS301',
                'credit': 3,
                'category': 'BUS',
                'description': 'Marketing strategies, consumer behavior, and market analysis.',
                'availability': True,
                'courses_allowed': 50
            },
            {
                'name': 'Digital Art Fundamentals',
                'code': 'ART101',
                'credit': 3,
                'category': 'ART',
                'description': 'Introduction to digital art tools, techniques, and creative processes.',
                'availability': True,
                'courses_allowed': 30
            },
            {
                'name': 'Web Design',
                'code': 'ART201',
                'credit': 3,
                'category': 'ART',
                'description': 'Web design principles, HTML, CSS, and user experience design.',
                'availability': True,
                'courses_allowed': 40
            },
            {
                'name': 'Data Structures and Algorithms',
                'code': 'CS401',
                'credit': 4,
                'category': 'CS',
                'description': 'Advanced data structures, algorithm analysis, and problem-solving techniques.',
                'availability': True,
                'courses_allowed': 30
            },
            {
                'name': 'Software Engineering',
                'code': 'CS501',
                'credit': 3,
                'category': 'CS',
                'description': 'Software development methodologies, project management, and quality assurance.',
                'availability': True,
                'courses_allowed': 25
            }
        ]

        # Create modules
        created_count = 0
        for module_data in modules_data:
            module, created = Module.objects.get_or_create(
                code=module_data['code'],
                defaults=module_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created module: {module.name} ({module.code})')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new modules')
        ) 