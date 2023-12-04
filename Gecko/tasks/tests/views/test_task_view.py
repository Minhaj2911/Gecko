"""Tests of the create task view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskForm
from tasks.models import User, Team, Task
from tasks.tests.helpers import LogInTester
from django.utils import timezone

class CreateTaskViewTestCase(TestCase, LogInTester):
    """Tests of the create task view."""
    
    fixtures = ['tasks/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.url = reverse('create_task')
        self.user = User.objects.get(username= '@johndoe')
        self.login_test_user(self.user)
        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Gecko research project',
            admin= self.user

         )
        self.team.members.add(self.user)

        self.form_input = {
            'title': 'Project meeting',
            'description': 'Conduct a meeting to discuss the new project design',
            'assignee': self.user,
            'due_date': timezone.now() + timezone.timedelta(days= 3),
            'status': 'assigned'
        }

        def test_get_create_task(self):
            response = self.client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'create_task.html')
        

        def valid_create_task_post(self):
            self.form_input = {
            'title': 'Project meeting',
            'description': 'Conduct a meeting to discuss the new project design',
            'assignee': self.user,
            'due_date': timezone.now() + timezone.timedelta(days= 3),
            'status': 'assigned'
        }