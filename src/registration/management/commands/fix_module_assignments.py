from django.core.management.base import BaseCommand
from registration.models import Module, Course

class Command(BaseCommand):
    help = 'Fix module course assignments'

    def handle(self, *args, **options):
        # Get the Arts course
        try:
            arts_course = Course.objects.get(name__icontains='art')
            self.stdout.write(self.style.SUCCESS(f'Found Arts course: {arts_course}'))
            
            # Get the Web Design module (case insensitive search)
            web_module = Module.objects.filter(name__icontains='web').first()
            if not web_module:
                self.stdout.write(self.style.ERROR('Web Design module not found'))
                return
                
            self.stdout.write(f'Found Web Design module: {web_module}')
            
            # Add the module to the Arts course if not already assigned
            if arts_course not in web_module.courses.all():
                web_module.courses.add(arts_course)
                self.stdout.write(self.style.SUCCESS(f'Added Web Design module to Arts course'))
            else:
                self.stdout.write('Web Design module is already assigned to Arts course')
                
        except Course.DoesNotExist:
            self.stdout.write(self.style.ERROR('Arts course not found'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
