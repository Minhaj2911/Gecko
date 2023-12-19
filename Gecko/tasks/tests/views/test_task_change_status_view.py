"""Test of the change status view."""
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskStatusForm
from tasks.models import User, Task, Team
from django.utils import timezone

class ChangeTaskStatusViewTest(TestCase):
    """Test of the change status view."""

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
            status='assigned'#,
            # team_of_task=self.team # comment out once merged to main
        )

        self.url = reverse('change_task_status', kwargs={'pk':self.task.pk})

        self.form_input = {'status': 'completed'}
    
    def test_change_task_status_url(self):
        self.assertEqual(self.url,f'/change_task_status/{self.task.pk}')
    
    def test_get_change_task_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change_status.html')
        form = response.context['form']
        task = response.context['task']
        self.assertTrue(isinstance(form, TaskStatusForm))
        self.assertEqual(self.task, task)
        self.assertFalse(form.is_bound)

    def test_succesful_task_status_change(self):
        self.client.post(self.url, self.form_input)
        updated_task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'completed')
    
    def test_successful_change_task_status_redirect(self):
        response= self.client.post(self.url, self.form_input, follow= True)
        response_url= reverse('task_dashboard')
        self.assertRedirects(response, response_url, status_code= 302, target_status_code= 200)
        self.assertTemplateUsed(response, 'task_dashboard.html')
        updated_task = Task.objects.get(pk=self.task.pk)
        self.assertEqual(updated_task.status, 'completed')


    