"""Test of the change status view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskStatusForm
from tasks.models import User, Task, Team
from django.utils import timezone

class ChangeTaskStatusViewTest(TestCase):
    """Test of the change status view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('change_task_status')
        self.user = User.objects.get(username='@johndoe')
        self.client.force_login(self.user)
        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Gecko research project',
            admin= self.user

         )
        
        self.team.members.add(self.user)

        self.task = Task.objects.create(
            title='Kick-off meeting',
            description='Conduct a meeting to get to know your team members.',
            assignee=self.user,
            due_date=timezone.now() + timezone.timedelta(days=7),
            status='assigned',
            # team_of_task=self.team # comment out once merged to main
        )
        
    