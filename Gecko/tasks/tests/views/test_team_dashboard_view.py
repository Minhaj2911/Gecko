"""Tests of the team dashboard view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team

class TeamDashboardViewTestCase(TestCase):
    """Tests of the team dashboard view."""
    
    fixtures = ['tasks/tests/fixtures/default_user.json']
    
    def setUp(self):
        self.url = reverse('dashboard')
        self.user = User.objects.get(username= '@johndoe')
        self.client.force_login(self.user)
        self.team= Team.objects.create(
            name= 'Gecko',
            description= 'Gecko research project',
            admin= self.user

         )
        self.team.members.add(self.user)
    
    def test_dashboard_url(self):
        self.assertEqual(self.url, "/dashboard/")
    
    def test_get_dashboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertIn('user_teams', response.context)   
        user_teams = response.context['user_teams']
        self.assertIn(self.team, user_teams)