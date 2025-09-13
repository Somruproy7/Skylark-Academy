from django.core.management.base import BaseCommand
from registration.models import Course
from django.utils import timezone
from datetime import date

class Command(BaseCommand):
    help = 'Populate sample course data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample courses...')
        
        # Create sample courses
        courses_data = [
            {
                'name': 'Bachelor of Computer Science',
                'code': 'BSCS',
                'category': 'CS',
                'description': 'A comprehensive program covering programming, algorithms, software engineering, and computer systems. Students learn modern programming languages, data structures, and software development methodologies.',
                'duration_years': 4,
                'total_credits': 480,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Mathematics',
                'code': 'BSMATH',
                'category': 'MATH',
                'description': 'Advanced study of pure mathematics, applied mathematics, statistics, and mathematical modeling. Prepares students for careers in research, finance, and data science.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Engineering',
                'code': 'BSE',
                'category': 'ENG',
                'description': 'Comprehensive engineering program covering mechanical, electrical, civil, and chemical engineering principles. Focuses on practical applications and problem-solving.',
                'duration_years': 4,
                'total_credits': 480,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Business Administration',
                'code': 'BBA',
                'category': 'BUS',
                'description': 'Business administration program covering management, finance, marketing, entrepreneurship, and business strategy. Prepares students for leadership roles in business.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Arts',
                'code': 'BA',
                'category': 'ART',
                'description': 'Liberal arts program focusing on visual arts, performing arts, design, and creative expression. Encourages artistic development and creative thinking.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Medicine',
                'code': 'MBBS',
                'category': 'MED',
                'description': 'Medical degree program preparing students for careers in healthcare. Covers anatomy, physiology, pathology, and clinical practice.',
                'duration_years': 6,
                'total_credits': 720,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Laws',
                'code': 'LLB',
                'category': 'LAW',
                'description': 'Law degree program covering legal principles, constitutional law, criminal law, and civil procedure. Prepares students for legal practice.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Education',
                'code': 'BED',
                'category': 'EDU',
                'description': 'Education degree program preparing students for teaching careers. Covers educational psychology, curriculum development, and teaching methods.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Science',
                'code': 'BSC',
                'category': 'SCI',
                'description': 'General science program covering physics, chemistry, biology, and environmental science. Provides broad scientific knowledge and research skills.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
            {
                'name': 'Bachelor of Humanities',
                'code': 'BAH',
                'category': 'HUM',
                'description': 'Humanities program covering philosophy, history, literature, and cultural studies. Develops critical thinking and analytical skills.',
                'duration_years': 3,
                'total_credits': 360,
                'is_active': True,
            },
        ]
        
        created_count = 0
        for course_data in courses_data:
            course, created = Course.objects.get_or_create(
                code=course_data['code'],
                defaults=course_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created course: {course.name} ({course.code})')
            else:
                self.stdout.write(f'Course already exists: {course.name} ({course.code})')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new courses!')
        )
        
        # Create Django Groups for each course
        self.stdout.write('Creating Django Groups for courses...')
        for course in Course.objects.all():
            group = course.ensure_group_exists()
            if group:
                self.stdout.write(f'Created/verified group: {group.name} for {course.name}')
        
        self.stdout.write(
            self.style.SUCCESS('Course population completed successfully!')
        )
