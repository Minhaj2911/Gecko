from tasks.models import Task, User, Team
from django.test import TestCase
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

class TaskTest(TestCase):
    """Unit tests for the Task model."""

    def setUp(self):

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

        self.task= Task.objects.create(
            title= 'Project meeting',
            description= 'Conduct a meeting to discuss the new project design',
            assignee= self.user,
            due_date= timezone.now() + timezone.timedelta(days= 3),
            status= 'assigned',
            team_of_task= self.team
        )
    
    def test_title_cannot_be_blank(self):
        self.task.title= ''
        self._assert_task_is_invalid(self.task)
    
    def test_valid_default_status(self):
        self.task.status= 'assigned'
        self._assert_task_is_valid(self.task)
    
    def test_invalid_status(self):
        self.task.status= ' '
        self._assert_task_is_invalid(self.task)
    
    def test_valid_status_choice(self):
        valid_status_choices= ['assigned', 'in progress', 'completed']
        for status in valid_status_choices:
            self.task.status= status
            self._assert_task_is_valid(self.task)
    
    def test_valid_assignee(self):
        self.task.assignee= self.user
        self._assert_task_is_valid(self.task)
    
    def test_description_can_be_blank(self):
        self.task.description= ''
        self._assert_task_is_valid(self.task)
    
    def test_title_may_contain_50_characters(self):
        self.task.title= 'x' * 50
        self._assert_task_is_valid(self.task)
    
    def test_title_must_not_contain_more_than_50_characters(self):
        self.task.title= 'x' * 51
        self._assert_task_is_invalid(self.task)

    def test_description_may_contain_400_characters(self):
        self.task.description= 'x' * 400
        self._assert_task_is_valid(self.task)
    
    def test_description_must_not_contain_more_than_400_characters(self):
        self.task.description= 'x' * 401
        self._assert_task_is_invalid(self.task)
    
    def test_valid_future_due_date_assigment(self):
        valid_due_date= timezone.now() + timedelta(days= 15)
        self.task.due_date= valid_due_date
        self._assert_task_is_valid(self.task)
    
    def test_invalid_past_due_date_assigment(self):
        invalid_date= timezone.now() - timedelta(days= 22)
        self.task.due_date= invalid_date
        self._assert_task_is_invalid(self.task)

    def test_vali_team_of_task(self):
        self.task.team_of_task= self.team
        self._assert_task_is_valid(self.task)

    def test_team_of_task_cannot_be_null(self):
        self.task.team_of_task= None
        self._assert_task_is_invalid(self.task)

    def _assert_task_is_valid(self, task):
        try:
            task.full_clean()
        except ValidationError:
            self.fail('Test task should be valid')
        
    def _assert_task_is_invalid(self, task):
        with self.assertRaises(ValidationError):
            task.full_clean()
    
    #add tests for team_of_task field

    
