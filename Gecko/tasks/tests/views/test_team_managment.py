from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import Team  

class TeamManagementTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user('admin', password='password')
        self.other_user = User.objects.create_user('member', password='password')
        self.team = Team.objects.create(name="Test Team", admin=self.admin_user)
        self.team.members.add(self.admin_user, self.other_user)
        self.client.force_login(self.admin_user)

    def test_transfer_admin(self):
        url = reverse('transfer_admin', kwargs={'pk': self.team.pk})
        new_admin_data = {'new_admin': self.other_user.id}
        response = self.client.post(url, new_admin_data, follow=True)
        self.team.refresh_from_db()
        self.assertEqual(self.team.admin, self.other_user)
        self.assertRedirects(response, reverse('team_detail', kwargs={'team_id': self.team.pk}))

    def test_add_members(self):
        new_member = User.objects.create_user('newmember', password='password')
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        add_member_data = {'new_members': [new_member.id]}
        response = self.client.post(url, add_member_data, follow=True)
        self.assertIn(new_member, self.team.members.all())
        self.assertRedirects(response, reverse('team_detail', kwargs={'team_id': self.team.pk}))

    def test_remove_members(self):
        url = reverse('remove_members', kwargs={'pk': self.team.pk})
        remove_member_data = {'members_to_remove': [self.other_user.id]}
        response = self.client.post(url, remove_member_data, follow=True)
        self.assertNotIn(self.other_user, self.team.members.all())
        self.assertRedirects(response, reverse('team_detail', kwargs={'team_id': self.team.pk}))

    def test_leave_team(self):
        url = reverse('leave_team', kwargs={'pk': self.team.pk})
        self.client.force_login(self.other_user)
        response = self.client.post(url, follow=True)
        self.assertNotIn(self.other_user, self.team.members.all())
        self.assertRedirects(response, reverse('dashboard'))

    def test_delete_team(self):
        url = reverse('delete_team', kwargs={'pk': self.team.pk})
        response = self.client.post(url, follow=True)
        self.assertFalse(Team.objects.filter(pk=self.team.pk).exists())
        self.assertRedirects(response, reverse('team_detail'))






