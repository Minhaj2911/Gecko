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
            status='assigned',
            team_of_task = self.team.id,
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


    def test_dashboard_view_displays_user_teams_correctly(self):
        url = reverse('dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user = response.context['user']
        teams = response.context['teams']
        self.assertEqual(user, self.user)
        self.assertIn(self.team1, teams)
        self.assertIn(self.team2, teams)
        self.assertEqual(len(teams), 2)