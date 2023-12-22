from django.test import TestCase
from django.urls import reverse
from tasks.models import Task, User, Team
from datetime import timedelta
from django.utils import timezone

class TaskEditViewTest(TestCase):
    """Tests of the task edit view."""
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.team = Team.objects.create(name='Test Team', admin=self.user)
        self.task = Task.objects.create(
            title='Test Task',
            description='Task description', 
            assignee=self.user, 
            due_date=timezone.now(), 
            team_of_task=self.team,
        ) 
        self.client.force_login(self.user)

    def test_task_edit_view(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)

    def test_task_edit_view_post(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Edited Task')
        self.assertEqual(self.task.description, 'Edited description')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk})) 

    def test_task_edit_view_post_invalid(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': '',
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_task_edit_view_post_invalid_due_date(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now() - timedelta(days=1),
            'team_of_task': self.team.id,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_task_edit_view_post_invalid_team(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': 2,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_task_edit_view_post_invalid_assignee(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'Edited description',
            'assignee': 2,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())   

    def test_task_edit_view_post_invalid_status(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
            'status': 'invalid status',
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_task_edit_view_post_invalid_priority(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
            'priority': 'invalid priority',
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_task_edit_view_post_invalid_description(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'Edited Task',
            'description': 'x' * 401,
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_task_edit_view_post_invalid_title(self):
        url = reverse('task_edit', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {
            'title': 'x' * 51,
            'description': 'Edited description',
            'assignee': self.user.id,
            'due_date': timezone.now(),
            'team_of_task': self.team.id,
        })
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Test Task')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'task_edit.html')
        self.assertIn('form', response.context)
        self.assertEqual(response.context['form'].instance, self.task)
        self.assertFalse(response.context['form'].is_valid())

    def test_update_task_status(self):
        url = reverse('update_task_status', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'status': 'in progress'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'in progress')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_status_invalid(self):
        url = reverse('update_task_status', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'status': 'invalid status'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'assigned')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_priority(self):
        url = reverse('update_task_priority', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'priority': 'low'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.priority, 'low')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_priority_invalid(self):
        url = reverse('update_task_priority', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'priority': 'invalid priority'})
        self.task.refresh_from_db()
        self.assertEqual(self.task.priority, 'high')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_due_date(self):
        url = reverse('update_task_due_date', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'due_date': timezone.now() + timedelta(days=1)})
        self.task.refresh_from_db()
        self.assertEqual(self.task.due_date, timezone.now() + timedelta(days=1))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_due_date_invalid(self):
        url = reverse('update_task_due_date', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'due_date': timezone.now() - timedelta(days=1)})
        self.task.refresh_from_db()
        self.assertEqual(self.task.due_date, timezone.now())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk})) 

    def test_update_task_assignee(self):
        url = reverse('update_task_assignee', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'assignee': self.user.id})
        self.task.refresh_from_db()
        self.assertEqual(self.task.assignee, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_assignee_invalid(self):
        url = reverse('update_task_assignee', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'assignee': 2})
        self.task.refresh_from_db()
        self.assertEqual(self.task.assignee, self.user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_team(self):
        url = reverse('update_task_team', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'team_of_task': self.team.id})
        self.task.refresh_from_db()
        self.assertEqual(self.task.team_of_task, self.team)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    def test_update_task_team_invalid(self):
        url = reverse('update_task_team', kwargs={'pk': self.task.pk})
        response = self.client.post(url, {'team_of_task': 2})
        self.task.refresh_from_db()
        self.assertEqual(self.task.team_of_task, self.team)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('task_detail', kwargs={'pk': self.task.pk}))

    

    
        


