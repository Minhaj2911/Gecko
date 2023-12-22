from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User

class TeamManagementViewTests(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')
        self.other_user = User.objects.get(username='@janedoe')
        self.team = Team.objects.create(name='Test Team', admin=self.user)
        self.team.members.add(self.user, self.other_user)
        self.client.force_login(self.user)

    def test_transfer_admin(self):
        url = reverse('assign_new_admin', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'new_admin': self.other_user.id})
        
        self.team.refresh_from_db()
        self.assertEqual(self.team.admin, self.other_user)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_add_members(self):
        new_member = User.objects.create_user(username='new_member', password='testpassword')
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'new_members': [new_member.id]})
        
        self.team.refresh_from_db()
        self.assertIn(new_member, self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_remove_members(self):
        url = reverse('remove_members', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'members_to_remove': [self.other_user.id]})
        
        self.team.refresh_from_db()
        self.assertNotIn(self.other_user, self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_admin_leaves_and_new_admin_assigned(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('leave_team', kwargs={'pk': self.team.pk}))
        self.team.refresh_from_db()

        self.assertNotEqual(self.team.admin, self.user)
        self.assertNotIn(self.user, self.team.members.all())
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_last_member_leaves_deletes_team(self):
        user = User.objects.create_user(username='last_member', password='password')
        solo_team = Team.objects.create(name='Solo Team', admin=user)
        solo_team.members.add(user)

        self.client.force_login(user)
        response = self.client.post(reverse('leave_team', kwargs={'pk': solo_team.pk}))
        
        self.assertFalse(Team.objects.filter(pk=solo_team.pk).exists())
        self.assertRedirects(response, reverse('dashboard'), status_code=302, target_status_code=200)

    def test_leave_team_as_non_admin(self):
        self.client.force_login(self.other_user)
        url = reverse('leave_team', kwargs={'pk': self.team.pk})
        response = self.client.post(url)
        self.team.refresh_from_db()
        self.assertNotIn(self.other_user, self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_delete_team(self):
        url = reverse('delete_team', kwargs={'pk': self.team.pk})
        response = self.client.post(url)
        
        self.assertFalse(Team.objects.filter(pk=self.team.pk).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_team_detail(self):
        url = reverse('team_detail', kwargs={'pk': self.team.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_detail.html')

