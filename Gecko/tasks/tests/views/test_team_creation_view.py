"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import TeamForm
from tasks.models import User, Team
from tasks.tests.helpers import LogInTester

class TeamCreationViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('create_task')
        self.form_input = {
            'name': 'Team123',
            'members': [],
            'descripton': 'We are a team and we work well',

        }
        self.user = User.objects.get(username='@johndoe')

    def test_create_team_url(self):
        self.assertEqual(self.url,'/create_team/')

    def test_get_create_team(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TeamForm))
        self.assertFalse(form.is_bound)

    def test_get_create_team_redirects_when_logged_in(self):
        # self.client.login(username=self.user.username, password="Password123")  ## add the team being made
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsuccesful_create_team(self):
        self.form_input['name'] = ''
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_team.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, TeamForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_create_team(self):
        before_count = Team.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = Team.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        team = Team.objects.get(username='@janedoe')
        # self.assertEqual(user.first_name, 'Jane')
        # self.assertEqual(user.last_name, 'Doe')
        # self.assertEqual(user.email, 'janedoe@example.org')
        # is_password_correct = check_password('Password123', user.password)
        # self.assertTrue(is_password_correct)
        # self.assertTrue(self._is_logged_in())

    # def test_post_create_team_redirects_when_logged_in(self):
    #     self.client.login(username=self.user.username, password="Password123")
    #     before_count = User.objects.count()
    #     response = self.client.post(self.url, self.form_input, follow=True)
    #     after_count = User.objects.count()
    #     self.assertEqual(after_count, before_count)
    #     redirect_url = reverse('dashboard')
    #     self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
    #     self.assertTemplateUsed(response, 'dashboard.html')
