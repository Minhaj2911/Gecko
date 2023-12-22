from django.urls import reverse
from tasks.models import Team, User
from django.contrib.messages import get_messages
from django.test import TestCase, RequestFactory
from tasks.forms import AddMembersForm
from tasks.views import add_members

class AddMembersViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin = User.objects.create_user(username='admin', password='password')
        self.team = Team.objects.create(name='Test Team', admin=self.admin)

    def test_add_members_as_admin(self):
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        request = self.factory.post(url, {'new_members': [1, 2, 3]})
        request.user = self.admin
        response = add_members(request, self.team.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invite to join team has been sent.')

    def test_add_members_as_non_admin(self):
        url = reverse('add_members', kwargs={'pk': self.team.pk})
        request = self.factory.post(url, {'new_members': [1, 2, 3]})
        non_admin = User.objects.create_user(username='non_admin', password='password')
        request.user = non_admin
        response = add_members(request, self.team.pk)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('team_detail', kwargs={'pk': self.team.pk}))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Only the admin can add members.')

    def test_add_members_invalid_form(self):
       url = reverse('add_members', kwargs={'pk': self.team.pk})
       request = self.factory.post(url, {'new_members': [1, 2, 3]})
       request.user = self.admin
       response = add_members(request, self.team.pk)
       self.assertEqual(response.status_code, 200)
       self.assertTemplateUsed(response, 'add_members.html')
       form = response.context['form']
       self.assertIsInstance(form, AddMembersForm)
       self.assertFalse(form.is_valid())
       
    def test_add_members_get_request(self):
       url = reverse('add_members', kwargs={'pk': self.team.pk})
       request = self.factory.get(url)
       request.user = self.admin
       response = add_members(request, self.team.pk)
       self.assertEqual(response.status_code, 200)
       self.assertTemplateUsed(response, 'add_members.html')
       form = response.context['form']
       self.assertIsInstance(form, AddMembersForm)
       self.assertTrue(form.is_bound)
       self.assertEqual(form.team_members, [self.admin.id])

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
