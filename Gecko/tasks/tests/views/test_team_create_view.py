from django.test import TestCase
from django.urls import reverse
from django.contrib import messages
from tasks.models import Team, User

class TeamCreateViewTests(TestCase):
    """ Test Team Create view. """
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json']

    def test_valid_form_submission_creates_team(self):
        before_count = Team.objects.count()
        form_data = {
            'name': 'Test Team',
            'description': 'This is a test',
            'members': [self.member.id],  
        }
        response = self.client.post(self.url, form_data)
        after_count = Team.objects.count()

        self.assertEqual(after_count, before_count + 1)
        self.assertEqual(response.status_code, 302)
        new_team = Team.objects.latest('id')
        self.assertRedirects(response, reverse('dashboard', kwargs={'pk': new_team.pk}))

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

    def setUp(self):
        self.user = User.objects.get(username= '@johndoe')
        self.member = User.objects.get(username='@janedoe')
        self.client.force_login(self.user)
        self.url = reverse('create_team')

    def test_valid_form_submission_creates_team(self):
        form_data = {
            'name': 'Test Team',
            'description': 'This is a test',
            'members': [self.member.id],
        }
        response = self.client.post(self.url, form_data)
        
        self.assertEqual(Team.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard', kwargs={'pk': 1}))
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "Successful: Team Created")

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

