"""Tests of the team dashboard view."""
from django.test import TestCase
from django.urls import reverse
from tasks.models import User, Team

class DashboardViewTestCase(TestCase):
    """Tests of the dashboard view."""
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
        self.client.force_login(self.user)
        response = self.client.get(reverse('dashboard'))
        self.assertIn('teams', response.context)
        self.assertIn(self.team, response.context['teams'])