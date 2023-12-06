from django.test import TestCase
from tasks.models import User, Task
from tasks.forms import TaskStatusForm
from django.utils import timezone
from django.test import TestCase
from .test_task_form import TaskFormTestCase


class TaskStatusFormTestCase(TestCase):
    """Unit tests of the task status form."""

    def setUp(self):
        super(TestCase, self).setUp()
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )

        self.task = Task.objects.create(
            title='Kick-off meeting',
            description='Conduct a meeting to get to know your team members.',
            assignee=self.user,
            due_date=timezone.now() + timezone.timedelta(days=7),
            status='assigned'
        )

        self.form_input = {'status': 'completed'}
    
    def test_status_form_has_necessary_fields(self):
        form = TaskStatusForm()
        self.assertIn('status', form.fields)
    
    def test_valid_task_status_form(self):
        form= TaskStatusForm(data=self.form_input)
        self.assertTrue(form.is_valid())
    
    #not sure about this
    def test_task_status_form_initialization(self):
        form = TaskStatusForm(data=self.form_input)
        self.assertFalse(form.instance.existing_task)

    def test_status_form_must_save_correctly(self):
        form = TaskStatusForm(instance=self.task, data=self.form_input)
        before_count = Task.objects.count()
        form.save()
        after_count = Task.objects.count()
        self.assertEqual(after_count, before_count)
        updated_task = Task.objects.get(title='Kick-off meeting')
        self.assertEqual(updated_task.description, 'Conduct a meeting to get to know your team members.')
        self.assertEqual(updated_task.assignee, self.user)
        valid_due_date= timezone.now() + timezone.timedelta(days= 7)
        date_test = TaskFormTestCase()
        date_test.assert_equal_due_date(updated_task.due_date, valid_due_date)
        self.assertEqual(updated_task.status, 'completed')
