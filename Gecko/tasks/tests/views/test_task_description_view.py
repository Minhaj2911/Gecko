"""Test of the task description view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskStatusForm
from tasks.models import User, Task
from django.utils import timezone


class TaskDescriptionViewTest(TestCase):
    """Test of the task description view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('task_description')
        self.user = User.objects.get(username='@johndoe')
        self.client.force_login(self.user)
        self.task = Task.objects.create(
            title='Kick-off meeting',
            description='Conduct a meeting to get to know your team members.',
            assignee=self.user,
            due_date=timezone.now() + timezone.timedelta(days=7),
            status='assigned'
        )
    

    