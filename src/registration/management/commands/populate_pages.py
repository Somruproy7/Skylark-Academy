from django.core.management.base import BaseCommand
from registration.models import PageContent

class Command(BaseCommand):
    help = 'Populate database with initial page content'

    def handle(self, *args, **options):
        # Sample page content data
        pages_data = [
            {
                'page': 'home',
                'title': 'Welcome to University Registration System',
                'content': '''
                <h1>Welcome to the University Registration System</h1>
                <p>This is your gateway to academic excellence. Browse through our diverse range of modules and courses designed to enhance your knowledge and skills.</p>
                
                <div class="features">
                    <h2>Key Features:</h2>
                    <ul>
                        <li>Easy module registration</li>
                        <li>Comprehensive course catalog</li>
                        <li>Student profile management</li>
                        <li>Real-time availability updates</li>
                    </ul>
                </div>
                
                <p>Get started by exploring our modules or creating your student account today!</p>
                '''
            },
            {
                'page': 'about',
                'title': 'About Our University',
                'content': '''
                <h1>About Our University</h1>
                <p>We are committed to providing high-quality education and fostering academic excellence. Our institution offers a wide range of programs across various disciplines.</p>
                
                <h2>Our Mission</h2>
                <p>To empower students with knowledge, critical thinking skills, and practical experience needed for success in their chosen fields.</p>
                
                <h2>Our Vision</h2>
                <p>To be a leading educational institution recognized for innovation, research, and student success.</p>
                
                <h2>Core Values</h2>
                <ul>
                    <li>Excellence in education</li>
                    <li>Innovation and creativity</li>
                    <li>Diversity and inclusion</li>
                    <li>Community engagement</li>
                </ul>
                '''
            },
            {
                'page': 'contact',
                'title': 'Contact Us',
                'content': '''
                <h1>Contact Us</h1>
                <p>We're here to help! Get in touch with us for any questions or support you need.</p>
                
                <div class="contact-info">
                    <h2>Contact Information</h2>
                    <p><strong>Address:</strong> 123 University Avenue, City, State 12345</p>
                    <p><strong>Phone:</strong> (555) 123-4567</p>
                    <p><strong>Email:</strong> info@university.edu</p>
                    <p><strong>Hours:</strong> Monday - Friday, 8:00 AM - 6:00 PM</p>
                </div>
                
                <div class="support">
                    <h2>Technical Support</h2>
                    <p>For technical issues with the registration system:</p>
                    <p><strong>Email:</strong> support@university.edu</p>
                    <p><strong>Phone:</strong> (555) 123-4568</p>
                </div>
                '''
            },
            {
                'page': 'modules_list',
                'title': 'Available Modules',
                'content': '''
                <h1>Available Modules</h1>
                <p>Explore our comprehensive selection of modules across various academic disciplines. Each module is designed to provide you with valuable knowledge and skills.</p>
                
                <div class="categories">
                    <h2>Module Categories</h2>
                    <ul>
                        <li><strong>Computer Science (CS):</strong> Programming, algorithms, software engineering</li>
                        <li><strong>Mathematics (MATH):</strong> Calculus, algebra, statistics</li>
                        <li><strong>Engineering (ENG):</strong> Mechanical, electrical, civil engineering</li>
                        <li><strong>Business (BUS):</strong> Management, accounting, marketing</li>
                        <li><strong>Arts (ART):</strong> Digital art, design, creative processes</li>
                    </ul>
                </div>
                
                <p>Browse through the modules below to find the perfect courses for your academic journey.</p>
                '''
            }
        ]

        # Create or update page content
        created_count = 0
        updated_count = 0
        
        for page_data in pages_data:
            page, created = PageContent.objects.get_or_create(
                page=page_data['page'],
                defaults=page_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created page: {page.get_page_display()}')
                )
            else:
                # Update existing content
                page.title = page_data['title']
                page.content = page_data['content']
                page.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated page: {page.get_page_display()}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {created_count + updated_count} pages ({created_count} created, {updated_count} updated)')
        )
