from django.test import TestCase
from tasks.models import User
from tasks.forms import AddMembersForm

class MemberFormsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')
        self.user3 = User.objects.create_user(username='user3', email='user3@example.com', password='testpass123')
        self.current_team_members = User.objects.filter(username='user1')
        self.non_team_members = User.objects.exclude(id__in=self.current_team_members)

    def test_add_members_form_initialization(self):
        form = AddMembersForm(team_members=self.current_team_members)
        expected_queryset = self.non_team_members
        self.assertQuerysetEqual(form.fields['new_members'].queryset, expected_queryset, ordered=False)

    def test_add_members_form_validation(self):
        form = AddMembersForm(data={'new_members': [self.user3.id]}, team_members=self.current_team_members)
        self.assertTrue(form.is_valid())
        form = AddMembersForm(data={'new_members': [self.user1.id]}, team_members=self.current_team_members)
        self.assertFalse(form.is_valid())
