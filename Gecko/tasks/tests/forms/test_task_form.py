"""Unit tests of the task form."""
from django.test import TestCase
from tasks.models import User, Task, Team
from tasks.forms import TaskForm
from django.utils import timezone
from datetime import timedelta, datetime
from django import forms

class TaskFormTestCase(TestCase):
    """Unit tests of the task form."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )
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
            'status': 'assigned',
            'priority': 2,
        }

    def test_valid_task_form(self):
        form= TaskForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_form_has_necessary_fields(self):
        form= TaskForm()
        self.assertIn('title', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('assignee', form.fields)
        due_date_field = form.fields['due_date']
        self.assertTrue(isinstance(due_date_field, forms.DateTimeField))
        self.assertIn('status', form.fields)
    
    def test_form_rejects_blank_title(self):
        self.form_input['title']= ''
        form= TaskForm(data= self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_past_due_date(self):
        self.form_input['due_date']= timezone.now() - timedelta(days= 1)
        form= TaskForm(data= self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_non_member_assignee(self):
        non_team_member_user= User.objects.create_user(
            username= '@jane123', 
            first_name='Jane',
            last_name='Smith',
            email='jane123smith@example.org'
            )
        invalid_form_input = {
            'title': 'Project meeting',
            'description': 'Conduct a meeting to discuss the new project design',
            'assignee': non_team_member_user.id,
            'due_date': timezone.now() + timezone.timedelta(days= 3),
            'status': 'assigned'
        }
        form= TaskForm(data= invalid_form_input, user=self.user)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_invalid_status(self):
        self.form_input['status']= ' '
        form= TaskForm(data= self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_accepts_valid_status(self):
        self.form_input['status']= 'completed'
        form= TaskForm(data= self.form_input)
        self.assertTrue(form.is_valid())
    
    def test_form_must_save_correctly(self):
        form= TaskForm(data= self.form_input)
        self.assertTrue(form.is_valid())
        before_count = Task.objects.count()
        form.save()
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count+1)
        task= Task.objects.get(title= 'Project meeting')
        self.assertEqual(task.description, 'Conduct a meeting to discuss the new project design')
        self.assertEqual(task.assignee, self.user)
        valid_due_date= timezone.now() + timezone.timedelta(days= 3)
        self.assert_equal_due_date(task.due_date, valid_due_date)
        self.assertEqual(task.status, self.form_input['status'])
    
    # def test_form_allows_editing_existing_form(self):
    #     existing_form= TaskForm(data= self.form_input)
    #     self.assertTrue(existing_form.is_valid())
    #     existing_task= existing_form.save()
    #     edited_due_date= timezone.now() + timezone.timedelta(days= 4)
    #     edited_data= {
    #         'title': 'Review tasks',
    #         'description': 'Create checklist to review tasks',
    #         'assignee': self.user,
    #         'due_date': edited_due_date,
    #         'status': 'completed',
    #         'priority': 3,
    #     }
    #     updated_task= TaskForm(instance= existing_task,data= edited_data)
    #     self.assertTrue(updated_task.is_valid())
    #     updated_task.save()
    #     existing_task.refresh_from_db()
    #     self.assertEqual(existing_task.title, 'Review tasks')
    #     self.assertEqual(existing_task.description, 'Create checklist to review tasks')
    #     self.assertEqual(existing_task.assignee, self.user)
    #     self.assert_equal_due_date(existing_task.due_date, edited_due_date)
    #     self.assertEqual(existing_task.status, 'completed')

    def assert_equal_due_date(self, due_date , expected_due_date):
        self.assertEqual(due_date.year, expected_due_date.year)
        self.assertEqual(due_date.month, expected_due_date.month)
        self.assertEqual(due_date.day, expected_due_date.day)
        self.assertEqual(due_date.hour, expected_due_date.hour)
        self.assertEqual(due_date.minute, expected_due_date.minute)


