"""Tests of the create task view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TaskForm, TeamSelectForm
from tasks.models import User, Team, Task
from django.utils import timezone

class CreateTaskViewTestCase(TestCase):
    """Tests of the create task view."""
    
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

    def test_create_task_url(self):
        self.assertEqual(self.url, "/create_task/")
        
    def test_get_create_task(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')
    
    def test_select_team(self):
        select_team_setup = {
            'team': self.team.id,
            'select_team': 'Select Team'
        }
        response= self.client.post(self.url, select_team_setup)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')
    
    def test_successful_task_creation(self):
        self.client.post(self.url, {'team': self.team.id, 'select_team': 'Select Team'})
        self.form_input['team_id']= self.team.id
        self.form_input['create_task']= 'Save Task'
        before_count= Task.objects.count()
        response= self.client.post(self.url, self.form_input, follow= True)
        after_count= Task.objects.count()
        self.assertEqual(after_count, before_count+ 1)
        response_url= reverse('dashboard')
        self.assertRedirects(response, response_url, status_code= 302, target_status_code= 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        task= Task.objects.get(title= self.form_input['title'])
        self.assertEqual(task.description, self.form_input['description'])
        self.assertEqual(task.assignee.id, self.user.id)
        self.assertEqual(task.status, self.form_input['status'])
    
    def test_invalid_due_date_task_creation(self):
        self.client.post(self.url, {'team': self.team.id, 'select_team': 'Select Team'})
        self.form_input['team_id']= self.team.id
        self.form_input['create_task']= 'Save Task'
        self.form_input['due_date']= timezone.now() - timezone.timedelta(days= 2)
        before_count= Task.objects.count()
        response= self.client.post(self.url, self.form_input)
        after_count= Task.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')

    def test_blank_title_task_creation(self):
        self.client.post(self.url, {'team': self.team.id, 'select_team': 'Select Team'})
        self.form_input['team_id']= self.team.id
        self.form_input['create_task']= 'Save Task'
        self.form_input['title']= ''
        response= self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')

    def test_no_assignee_task_creation(self):
        self.client.post(self.url, {'team': self.team.id, 'select_team': 'Select Team'})
        self.form_input['team_id']= self.team.id
        self.form_input['create_task']= 'Save Task'
        self.form_input['assignee']= ''
        response= self.client.post(self.url, self.form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_task.html')
    
    def test_successful_create_task_redirect(self):
        correct_form_input = {
            'team_id': self.team.id,
            'create_task': 'Save Task',
            'title': 'Project meeting',
            'description': 'Conduct a meeting to discuss the new project design',
            'assignee': self.user.id,
            'due_date': timezone.now() + timezone.timedelta(days= 3),
            'status': 'assigned'
        }
        response= self.client.post(self.url, correct_form_input, follow= True)
        response_url= reverse('dashboard')
        self.assertRedirects(response, response_url, status_code= 302, target_status_code= 200)
        self.assertTemplateUsed(response, 'dashboard.html')

    #add tests for no team_of_task field ?? for blank true and null true   