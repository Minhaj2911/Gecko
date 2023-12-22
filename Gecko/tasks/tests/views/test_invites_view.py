from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib import messages
from tasks.models import Team
from tasks.views import InvitesView

class TestInvitesView(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username='test', email='test@example.com', password='test')
        self.team = Team.objects.create(name='test_team')
        self.user.invites.add(self.team)

    def test_team_invites(self):
        request = self.factory.get('/invites')
        request.user = self.user

        response = InvitesView.team_invites(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.team, response.context_data['user_invites'])

    def test_join_team(self):
        request = self.factory.post('/join_team/test_team')
        request.user = self.user

        response = InvitesView.join_team(request, 'test_team')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.team, request.user.teams.all())
        self.assertNotIn(self.team, request.user.invites.all())
        self.assertIn(self.user, self.team.members.all())
        self.assertEqual(len(messages.get_messages(request)), 1)

    def test_reject_invite(self):
        request = self.factory.post('/reject_invite/test_team')
        request.user = self.user

        response = InvitesView.reject_invite(request, 'test_team')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.team, request.user.invites.all())
        self.assertEqual(len(messages.get_messages(request)), 1)