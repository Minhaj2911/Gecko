from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from tasks.models import Task
from tasks.views import task_dashboard

class TaskDashboardViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='testpass123')
        self.task1 = Task.objects.create(title='Task 1', assignee=self.user)
        self.task2 = Task.objects.create(title='Task 2', assignee=self.user)
        self.task3 = Task.objects.create(title='Task 3', assignee=self.user)

    def test_task_dashboard_with_search_input(self):
        request = self.factory.get('/task_dashboard/', {'search_input': 'Task 1'})
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 3')

    def test_task_dashboard_with_form_data(self):
        request = self.factory.get('/task_dashboard/', {'title': 'Task 1', 'status': 'In Progress'})
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertNotContains(response, 'Task 2')
        self.assertNotContains(response, 'Task 3')

    def test_task_dashboard_with_sort_by(self):
        request = self.factory.get('/task_dashboard/', {'sort_by': 'title'})
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')
        self.assertContains(response, 'Task 3')

    def test_task_dashboard_without_search_input_and_form_data(self):
        request = self.factory.get('/task_dashboard/')
        request.user = self.user
        response = task_dashboard(request)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Task 1')
        self.assertContains(response, 'Task 2')
        self.assertContains(response, 'Task 3')