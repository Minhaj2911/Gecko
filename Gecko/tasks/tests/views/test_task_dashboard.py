"""Test of the task dashboard view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Task
from django.utils import timezone

class TaskDashboardViewTest(TestCase):
    """Test of the task dashboard view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('task_dashboard')
        self.user = User.objects.get(username='@johndoe')
        self.client.force_login(self.user)
        self.task = Task.objects.create(
            title='Kick-off meeting',
            description='Conduct a meeting to get to know your team members.',
            assignee=self.user,
            due_date=timezone.now() + timezone.timedelta(days=7),
            status='assigned'
        )
    
    def test_task_dashboard_url(self):
        self.assertEqual(self.url, "/task_dashboard/")
    

    def test_get_task_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_dashboard.html')

        
    def test_dashboard_view_with_logged_in_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('task_dashboard'))
        self.assertEqual(response.status_code, 200) 