"""Tests for the forgotten password. """
from django.test import TestCase
from django.urls import reverse
from tasks.models import User
from django.core import mail

class PasswordResetTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='old_password')

    def test_password_reset_form(self):
        response = self.client.post(reverse('password_reset'), {'email': 'test@example.com'})
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('password_reset_done'))

    def test_password_reset_email_sent(self):
        self.client.post(reverse('password_reset'), {'email': 'test@example.com'})
        self.assertEqual(len(mail.outbox), 1) 
        self.assertIn('test@example.com', mail.outbox[0].to)  

    def test_password_reset_confirm_and_complete(self):
        user = User.objects.get(username='@johndoe')
        user.is_active = False
        user.save()
        self.client.post(reverse('password_reset'), {'email': user.email})
        self.assertEqual(len(mail.outbox), 1)
        email_body = mail.outbox[0].body
        url_token = email_body.split('reset/')[1].split('/')[1].split('\n')[0]
        uid = email_body.split('reset/')[1].split('/')[0]
        response = self.client.get(reverse('password_reset_confirm', args=(uid, url_token)))
        self.assertEqual(response.status_code, 200)
        response = self.client.post(reverse('password_reset_confirm', args=(uid, url_token)), {
            'new_password1': 'new_password',
            'new_password2': 'new_password'
        })
        self.assertRedirects(response, reverse('password_reset_complete'))
        self.assertTrue(self.client.login(username='@johndoe', password='new_password'))