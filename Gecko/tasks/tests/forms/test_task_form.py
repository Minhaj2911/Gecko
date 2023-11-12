"""Unit tests of the task form."""
from django.test import TestCase
from tasks.models import User, Task
from tasks.forms import TaskForm
from django.utils import timezone
from datetime import timedelta, datetime
from django import forms

class TaskFormTestCase(TestCase):
    """Unit tests of the task form."""

    ##user should be replaced with a team member from a group
    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )
        self.form_input = {
            'title': 'Project meeting',
            'description': 'Conduct a meeting to discuss the new project design',
            'assignee': self.user,
            'due_date': timezone.now() + timezone.timedelta(days= 3)
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
    
    def test_form_rejects_blank_title(self):
        self.form_input['title']= ''
        form= TaskForm(data= self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_past_due_date(self):
        self.form_input['due_date']= timezone.now() - timedelta(days= 1)
        form= TaskForm(data= self.form_input)
        self.assertFalse(form.is_valid())
    
    def test_form_rejects_no_assignee(self):
        self.form_input['assignee']= None
        form= TaskForm(data= self.form_input)
        self.assertFalse(form.is_valid())
    
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
        expected_due_date= timezone.now() + timezone.timedelta(days= 3)
        self.assertEqual(task.due_date.year, expected_due_date.year)
        self.assertEqual(task.due_date.month, expected_due_date.month)
        self.assertEqual(task.due_date.day, expected_due_date.day)
        self.assertEqual(task.due_date.hour, expected_due_date.hour)
    
    def test_form_allows_editing_existing_form(self):
        existing_form= TaskForm(data= self.form_input)
        self.assertTrue(existing_form.is_valid())
        existing_task= existing_form.save()
        edited_data= {
            'title': 'Review tasks',
            'description': 'Create checklist to review tasks',
            'assignee': self.user,
            'due_date': timezone.now() + timezone.timedelta(days= 4)
        }
        updated_task= TaskForm(instance= existing_task,data= edited_data)
        self.assertTrue(updated_task.is_valid())
        updated_task.save()
        existing_task.refresh_from_db()
        self.assertEqual(existing_task.title, 'Review tasks')
        self.assertEqual(existing_task.description, 'Create checklist to review tasks')
        self.assertEqual(existing_task.assignee, self.user)
        self.assertEqual(existing_task.due_date.year, edited_data['due_date'].year)
        self.assertEqual(existing_task.due_date.month, edited_data['due_date'].month)
        self.assertEqual(existing_task.due_date.day, edited_data['due_date'].day)
        self.assertEqual(existing_task.due_date.hour, edited_data['due_date'].hour)


