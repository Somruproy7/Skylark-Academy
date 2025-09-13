from django.core.management.base import BaseCommand
from registration.models import Course, Module
import random


COURSE_WORDS = [
    "Nimbus", "Aurora", "Pinnacle", "Vertex", "Harbor", "Summit", "Cascade", "Atlas",
    "Zenith", "Odyssey", "Nova", "Halcyon", "Lyra", "Sable", "Cobalt", "Sierra",
]

MODULE_WORDS = [
    "Quantum", "Synergy", "Catalyst", "Vector", "Nimbus", "Aurora", "Matrix", "Pulse",
    "Vertex", "Harbor", "Flux", "Neon", "Echo", "Orbit", "Prism", "Circuit",
]


def generate_name(words: list[str]) -> str:
    left = random.choice(words)
    right = random.choice(words)
    if left == right:
        right = random.choice([w for w in words if w != left])
    return f"{left} {right}"


class Command(BaseCommand):
    help = "Randomize names for Courses and Modules"

    def add_arguments(self, parser):
        parser.add_argument("--only", choices=["courses", "modules"], default=None)

    def handle(self, *args, **options):
        only = options.get("only")

        if only in (None, "courses"):
            for course in Course.objects.all():
                old = course.name
                course.name = generate_name(COURSE_WORDS)
                course.save(update_fields=["name"])
                self.stdout.write(self.style.SUCCESS(f"Course {course.code}: '{old}' -> '{course.name}'"))

        if only in (None, "modules"):
            for module in Module.objects.all():
                old = module.name
                module.name = generate_name(MODULE_WORDS)
                module.save(update_fields=["name"])
                self.stdout.write(self.style.SUCCESS(f"Module {module.code}: '{old}' -> '{module.name}'"))

        self.stdout.write(self.style.NOTICE("Randomization complete."))


