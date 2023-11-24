from teams.models import Team, User
from django.test import TestCase
from datetime import timedelta, datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

class TeamTest(TestCase):
    """Unit tests for the team model."""

    def setUp(self):

        ##user should be replaced with a team member from a group
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )

        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Scientific reasearch into Geckos',
            admin= self.user
            #members= 
        )
    
    def test_team_name_cannot_be_blank(self):
        self.team.team_name= ''
        self._assert_team_is_invalid(self.team)

    def test_description_can_be_blank(self):
        self.team.description= ''
        self._assert_team_is_valid(self.team)

    def test_team_name_may_contain_50_characters(self):
        self.team.team_name= 'x' * 50
        self._assert_team_is_valid(self.team)

    def test_team_name_must_not_contain_51_characters(self):
        self.team.team_name= 'x' * 51
        self._assert_team_is_invalid(self.team)

    def test_description_may_contain_400_characters(self):
        self.team.description= 'x' * 400
        self._assert_team_is_valid(self.team)

    def test_description_must_not_contain_more_than_400_characters(self):
        self.team.description= 'x' * 401
        self._assert_team_is_invalid(self.team)

    def _assert_team_is_valid(self, team):
        try:
            team.full_clean()
        except ValidationError:
            self.fail('Test team should be valid')

    def _assert_team_is_invalid(self, team):
        with self.assertRaises(ValidationError):
            team.full_clean()