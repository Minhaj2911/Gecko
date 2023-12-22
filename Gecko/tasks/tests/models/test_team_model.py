from tasks.models import Team, User
from django.test import TestCase
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from tasks.models import Task

class TeamTest(TestCase):
    """Unit tests for the team model."""

    def setUp(self):

        ##user should be replaced with a team member from a group
        self.user_admin = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )
        self.user_1 = User.objects.create_user(
            '@johndoe1',
            first_name='Johna',
            last_name='Doe',
            email='johndoe1@example.org'
        )
        self.user_2 = User.objects.create_user(
            '@johndoe2',
            first_name='Johnb',
            last_name='Doe',
            email='johndoe2@example.org'
        )
        self.user_3 = User.objects.create_user(
            '@johndoe3',
            first_name='Johnc',
            last_name='Doe',
            email='johndoe3@example.org'
        )

        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Scientific reasearch into Geckos',
            admin= self.user_admin,
        )
        for user in [self.user_1, self.user_2, self.user_3, self.user_admin]:
            self.team.members.add(user)

    
    def test_team_name_cannot_be_blank(self):
        self.team.name= ''
        self._assert_team_is_invalid(self.team)

    def test_description_can_be_blank(self): 
        self.team.description= ''
        self._assert_team_is_valid(self.team)

    def test_team_name_may_contain_50_characters(self):
        self.team.name= 'x' * 50
        self._assert_team_is_valid(self.team)

    def test_team_name_must_not_contain_51_characters(self): 
        self.team.name= 'x' * 51
        self._assert_team_is_invalid(self.team)

    def test_description_may_contain_500_characters(self): 
        self.team.description= 'x' * 500
        self._assert_team_is_valid(self.team)

    def test_description_must_not_contain_more_than_500_characters(self): 
        self.team.description= 'x' * 501
        self._assert_team_is_invalid(self.team)
            
    def test_admin_must_not_be_blank(self):
        self.team.admin= None
        self._assert_team_is_invalid(self.team)

    # def test_members_must_not_be_blank(self):
    #     self.team.members.clear()
    #     self._assert_team_is_invalid(self.team)

    # def test_members_must_include_admin(self):
    #     print(str(self.team.members.all()))
    #     self.team.members.remove(self.user_admin)
    #     print(str(self.team.members.all()))
    #     self._assert_team_is_invalid(self.team)

    def _assert_team_is_valid(self, team):
        try:
            team.full_clean()
        except ValidationError:
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self, team):
        with self.assertRaises(ValidationError):
            team.full_clean()

    def test_get_members(self):
        expected_members = ",".join([str(member) for member in [self.user_admin, self.user_1, self.user_2, self.user_3]])
        self.assertEqual(self.team.get_members(), expected_members)

    def test_set_admin(self):
        new_admin = User.objects.create_user('@janedoe', first_name='Jane', last_name='Doe', email='janedoe@example.org')
        self.team.set_admin(new_admin)
        self.assertEqual(self.team.admin, new_admin)

    def test_get_tasks(self):
        task1 = Task.objects.create(title='Task 1', 
            description= 'Conduct a meeting to discuss the new project design',
            assignee= self.user_1, 
            due_date=datetime.now() + timedelta(days=4), 
            status= 'assigned',
            team_of_task= self.team)
        
        task2 = Task.objects.create(title='Task 2', 
            description= 'Review planning analysis',
            assignee= self.user_2, 
            due_date=timezone.now() + timezone.timedelta(days= 6), 
            status= 'assigned',
            team_of_task= self.team)

        self.team.tasks.add(task1, task2)

        expected_tasks = ",".join([str(task) for task in [task1, task2]])
        self.assertEqual(self.team.get_tasks(), expected_tasks)

