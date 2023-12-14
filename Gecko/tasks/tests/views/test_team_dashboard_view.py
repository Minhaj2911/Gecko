"""Tests of the team dashboard view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskForm, TeamSelectForm
from tasks.models import User, Team, Task
from django.utils import timezone

class CreateTaskViewTestCase(TestCase):
    """Tests of the team dashboard view"""
    
    fixtures = ['tasks/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.url = reverse('create_task')
        self.user = User.objects.get(username= '@johndoe')
        self.client.force_login(self.user)
        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Gecko research project',
            admin= self.user

         )
        self.team.members.add(self.user)

        self.form_input = {
            'title': 'Project meeting',
            'description': 'Conduct a meeting to discuss the new project design',
            'assignee': self.user.id,
            'due_date': timezone.now() + timezone.timedelta(days= 3),
            'status': 'assigned'
        }