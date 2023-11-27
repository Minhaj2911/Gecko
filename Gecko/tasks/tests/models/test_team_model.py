from tasks.models import Team, User
from django.test import TestCase
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

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
        for user in [self.user_1, self.user_2, self.user_3]:
            self.team.members.add(user)

    
    def test_team_name_cannot_be_blank(self): #
        self.team.name= ''
        self._assert_team_is_invalid(self.team)

    def test_description_can_be_blank(self): 
        self.team.description= ''
        self._assert_team_is_valid(self.team)

    def test_team_name_may_contain_50_characters(self):
        self.team.name= 'x' * 50
        self._assert_team_is_valid(self.team)

    def test_team_name_must_not_contain_51_characters(self): #
        self.team.name= 'x' * 51
        self._assert_team_is_invalid(self.team)

    def test_description_may_contain_500_characters(self): 
        self.team.description= 'x' * 500
        self._assert_team_is_valid(self.team)

    def test_description_must_not_contain_more_than_500_characters(self): #
        self.team.description= 'x' * 501
        self._assert_team_is_invalid(self.team)


    def test_is_user_admin_in_members(self):
        if self.user_admin not in self.team.members.all():
            self._assert_team_is_valid(self.team)
            

    def _assert_team_is_valid(self, team):
        try:
            team.full_clean()
        except ValidationError:
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self, team):
        with self.assertRaises(ValidationError):
            team.full_clean()
