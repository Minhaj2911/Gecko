from django.test import TestCase
from django.urls import reverse
from tasks.models import Team, User

class TeamManagementViewTests(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json', 'tasks/tests/fixtures/other_users.json']

    def setUp(self):
        self.user = User.objects.get(username='@johndoe')  
        self.other_user = User.objects.get(username='@janedoe')
        self.new_admin = User.objects.get(username='@petrapickles')
        self.new_member = User.objects.get(username='@peterpickles')
        self.team = Team.objects.create(name='Test Team', admin=self.user)
        self.team.members.add(self.user, self.other_user)
        self.admin_user = self.user 
        self.non_admin_user = self.other_user
        self.client.force_login(self.user)

    def test_successful_admin_transfer(self):
        url = reverse('assign_new_admin', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'new_admin': self.new_admin})
        self.assertEqual(self.team.admin, self.new_admin)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_no_action_on_get_request(self):
        url = reverse('assign_new_admin', kwargs={'pk': self.team.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'assign_new_admin.html')

    def test_non_admin_cannot_add_members(self):
        self.client.force_login(self.user)
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'new_members': [self.new_member.id]})
        
        self.team.refresh_from_db()
        self.assertFalse(self.new_member in self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_successful_member_addition(self):
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'new_members': [self.new_member.id]})
        
        self.team.refresh_from_db()
        self.assertTrue(self.new_member in self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_no_action_on_get_request(self):
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_members.html')

    def test_non_admin_cannot_remove_members(self):
        self.client.force_login(self.user)
        url = reverse('remove_members', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'members_to_remove': [self.admin_user.id]})
        
        self.team.refresh_from_db()
        self.assertTrue(self.admin_user in self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_successful_member_removal(self):
        url = reverse('remove_members', kwargs={'pk': self.team.pk})
        response = self.client.post(url, {'members_to_remove': [self.user.id]})
        
        self.team.refresh_from_db()
        self.assertFalse(self.user in self.team.members.all())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_no_action_on_get_request(self):
        initial_member_count = self.team.members.count()
        url = reverse('remove_members', kwargs={'pk': self.team.pk})
        response = self.client.get(url)

        self.team.refresh_from_db()
        self.assertEqual(self.team.members.count(), initial_member_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'remove_members.html')


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

    def test_redirect_to_dashboard_on_get_request(self):
        url = reverse('leave_team', kwargs={'pk': self.team.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard', kwargs={'pk': self.team.pk}))

    def test_delete_team_by_admin(self):
        self.client.force_login(self.admin_user)
        url = reverse('delete_team', kwargs={'pk': self.team.pk})
        response = self.client.post(url)
        
        self.assertFalse(Team.objects.filter(pk=self.team.pk).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_non_admin_user_cannot_delete_team(self):
        self.client.force_login(self.non_admin_user)
        url = reverse('delete_team', kwargs={'pk': self.team.pk})
        response = self.client.post(url)
        
        self.assertTrue(Team.objects.filter(pk=self.team.pk).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))

    def test_no_action_on_get_request(self):
        self.client.force_login(self.admin_user)
        url = reverse('delete_team', kwargs={'pk': self.team.pk})
        response = self.client.get(url)

        self.assertTrue(Team.objects.filter(pk=self.team.pk).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_team_detail(self):
        url = reverse('team_detail', kwargs={'pk': self.team.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'team_detail.html')

