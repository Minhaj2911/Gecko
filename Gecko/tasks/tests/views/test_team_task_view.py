"""Tests of the team task view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team, Task
from django.utils import timezone

class TeamTaskViewTestCase(TestCase):
    """Tests of the team task view."""
    fixtures = ['tasks/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.user = User.objects.get(username= '@johndoe')
        self.client.force_login(self.user)
        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Gecko research project',
            admin= self.user

         )
        self.team.members.add(self.user)
        self.url = reverse('team_tasks', kwargs={'pk':self.team.pk})

        self.task = Task.objects.create(title= 'Client meeting',
            description= 'Conduct a meeting with the client to discuss the outcomes of the project.',
            assignee= self.user,
            due_date= timezone.now() + timezone.timedelta(days= 3),
            status= 'assigned',
            team_of_task=self.team
        )
    
    def test_team_task_url(self):
        self.assertEqual(self.url,f'/team_tasks/{self.team.pk}/')
    
    def test_get_team_tasks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_tasks.html')
        self.assertIn('team', response.context)  
        self.assertIn('tasks', response.context) 
        team = response.context['team']
        tasks = response.context['tasks']
        self.assertEqual(self.team, team)
        self.assertIn(self.task, tasks)