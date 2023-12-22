from django.test import TestCase
from tasks.models import User, Team
from tasks.forms import InviteTeamMembersForm

class InviteTeamMembersFormTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='testpassword1')
        self.user2 = User.objects.create_user(username='user2', password='testpassword2')
        self.user3 = User.objects.create_user(username='user3', password='testpassword3')

        self.team = Team.objects.create(name='Test Team')
        self.team.members.add(self.user1)

    def test_invite_members(self):
        form_data = {'members': [self.user2.id, self.user3.id]}
        form = InviteTeamMembersForm(data=form_data, instance=self.team)
        self.assertTrue(form.is_valid())
        form.save(self.team)
        self.assertIn(self.user2, self.team.invites.all())
        self.assertIn(self.user3, self.team.invites.all())
        self.assertNotIn(self.user1, self.team.invites.all()) 

