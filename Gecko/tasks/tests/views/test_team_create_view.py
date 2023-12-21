from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from tasks.models import Team
from tasks.views import TeamCreateView 

class TeamCreateViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.member = User.objects.create_user(username='member', password='password')
        self.client.force_login(self.user)
        self.url = reverse('create_team') 

    def test_valid_form_submission_creates_team(self):
        form_data = {
            'name': 'New Team',
            'description': 'A new team for testing',
            'members': [self.member.id] 
        }
        response = self.client.post(self.url, form_data)
        
        self.assertEqual(Team.objects.count(), 1)
        team = Team.objects.first()
        self.assertEqual(team.name, 'New Team')
        self.assertEqual(team.admin, self.user)
        self.assertTrue(self.member in team.members.all())
        self.assertRedirects(response, reverse('dashboard'))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Team Created!")

    def test_invalid_form_submission_does_not_create_team(self):
        form_data = {
            'name': '',
            'description': 'This is a test' * 1000,
            'members': ['invalid'],
        }
        response = self.client.post(self.url, form_data)
        
        self.assertEqual(Team.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Unsuccessful: Team Not Created")

    def test_get_success_url(self):
        view = TeamCreateView()
        view.request = self.factory.get(self.url)
        self.assertEqual(view.get_success_url(), reverse('dashboard'))
