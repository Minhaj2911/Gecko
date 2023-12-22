from django.test import TestCase
from django.urls import reverse
from tasks.models import Task, User
from datetime import datetime, timedelta

class TaskEditViewTest(TestCase):
    """Tests of the task edit view."""
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.assignee = User.objects.get(username='@johndoe')
        due_date = datetime.now() + timedelta(days=10)
        self.task = Task.objects.create(
            title='Test Task', 
            description='This is a test task',
            due_date=due_date,
            assignee=self.assignee
        )

    def test_update_task(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'title': 'Updated Task', 'description': 'This task has been updated'})
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.description, 'This task has been updated')

    def test_update_task_invalid_data(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'title': '', 'description': ''})
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')  
        self.assertEqual(self.task.description, 'This is a test task')  
        
    def test_update_task_not_found(self):
        url = reverse('task_edit', kwargs={'pk': 9999}) 
        response = self.client.post(url, {'title': 'Updated Task', 'description': 'This task has been updated'})
        self.assertEqual(response.status_code, 404)

    def test_update_task_duplicate(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'title': 'Test Task', 'description': 'This is a test task'})
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task')

    def test_update_task_partial_data(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'title': 'Updated Task'})
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
        self.assertEqual(self.task.description, 'This is a test task')

    def test_update_task_empty_data(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(self.task.description, 'This is a test task')

