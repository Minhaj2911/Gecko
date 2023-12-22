from django.test import TestCase
from tasks.models import User
from tasks.forms import AssignNewAdminForm

class AssignNewAdminFormTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')
        self.team_members = User.objects.filter(username__in=['user1', 'user2'])

    def test_form_initialization(self):
        form = AssignNewAdminForm(team_members=self.team_members)
        self.assertEqual(set(form.fields['new_admin'].queryset), set(self.team_members))

    def test_form_validation_with_valid_data(self):
        form = AssignNewAdminForm(data={'new_admin': self.user1.id}, team_members=self.team_members)
        self.assertTrue(form.is_valid())

    def test_form_validation_with_invalid_data(self):
        non_member = User.objects.create_user(username='non_member', email='nonmember@example.com', password='testpass123')
        form = AssignNewAdminForm(data={'new_admin': non_member.id}, team_members=self.team_members)
        self.assertFalse(form.is_valid())
