"""Test of the task dashboard view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskStatusForm
from tasks.models import User, Task, Team
from django.utils import timezone
from tasks.tests.helpers import reverse_with_next

class TaskDashboardViewTest(TestCase):
    """Test of the task dashboard view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('task_dashboard')
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
            status='assigned'#,
            # team_of_task=self.team # comment out once merged to main
        )
    
    def test_task_dashboard_url(self):
        self.assertEqual(self.url, "/task_dashboard/")
    

    def test_get_task_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_dashboard.html')
        self.assertIn('user_tasks', response.context)
        self.assertIn('user', response.context)
        user_tasks = response.context['user_tasks']
        user = response.context['user']
        self.assertIn(self.task, user_tasks)
        self.assertEqual(self.user, user)
    
    #add tests for search functionality