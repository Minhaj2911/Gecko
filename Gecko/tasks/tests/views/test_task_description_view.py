"""Test of the task description view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Task, Team
from django.utils import timezone


class TaskDescriptionViewTest(TestCase):
    """Test of the task description view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
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
            team_of_task=self.team
        )
        self.url = reverse('task_description', kwargs={'pk':self.task.pk})

    def test_task_description_url(self):
        self.assertEqual(self.url,f'/task_description/{self.task.pk}/')
    
    def test_get_task_description(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_description.html')
        self.assertIn('task', response.context)
        task = response.context['task']
        self.assertEqual(self.task, task)
    

    