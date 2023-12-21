from django.core.management.base import BaseCommand, CommandError
from tasks.models import User, Task, Team

class Command(BaseCommand):
    """Build automation command to unseed the database."""
    
    help = 'Seeds the database with sample data'

    def handle(self, *args, **options):
        """Unseed the database."""

        User.objects.filter(is_staff=False).delete()
        Task.objects.all().delete()
        Team.objects.all().delete()