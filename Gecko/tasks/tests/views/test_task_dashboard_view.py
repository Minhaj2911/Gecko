from django.test import TestCase, RequestFactory
from django.urls import reverse
from tasks.models import User, Task, Team
from django.utils import timezone
from tasks.views import task_dashboard

class TaskDashboardViewTests(TestCase):
    """Tests of the task dashboard view."""
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.get(username='@johndoe')
        self.team_admin = User.objects.get(username='@janedoe')
        self.team = Team.objects.create(name='Test Team', admin=self.team_admin)
        Task.objects.create(title='Test Task 1', description='Task 1 description', assignee=self.user, team_of_task=self.team, due_date=timezone.now())
        Task.objects.create(title='Test Task 2', description='Task 2 description', assignee=self.user, team_of_task=self.team, due_date=timezone.now())

    def test_task_dashboard_with_current_user(self):
        request = self.factory.get(reverse('task_dashboard'))
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn('tasks', response.context)
        self.assertEqual(len(response.context['tasks']), 2) 

    def test_task_dashboard_search_functionality(self):
        request = self.factory.get(reverse('task_dashboard'), {'search_input': 'Task 1'})
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].title, 'Test Task 1')

    def test_task_dashboard_form_filter(self):
        form_data = {'title': 'Task 1', 'status': 'Open', 'due_date': timezone.now(), 'team_of_task': self.team.id, 'priority': 'High'}
        request = self.factory.get(reverse('task_dashboard'), form_data)
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].title, 'Test Task 1')

    def test_task_dashboard_form_filter_no_due_date(self):
        form_data = {'title': 'Task 1', 'status': 'Open', 'team_of_task': self.team.id, 'priority': 'High'}
        request = self.factory.get(reverse('task_dashboard'), form_data)
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(len(response.context['tasks']), 1)
        self.assertEqual(response.context['tasks'][0].title, 'Test Task 1')

    def test_task_dashboard_form_filter_no_results(self):
        form_data = {'title': 'Task 1', 'status': 'Open', 'due_date': timezone.now(), 'team_of_task': self.team.id, 'priority': 'Low'}
        request = self.factory.get(reverse('task_dashboard'), form_data)
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(len(response.context['tasks']), 0)

    def test_task_dashboard_sorting(self):
        request = self.factory.get(reverse('task_dashboard'), {'sort_by': 'title'})
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(len(response.context['tasks']), 2)
        self.assertEqual(response.context['tasks'][0].title, 'Test Task 1')


