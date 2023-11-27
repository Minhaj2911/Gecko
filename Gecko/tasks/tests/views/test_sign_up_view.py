"""Tests of the sign up view."""
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from tasks.forms import SignUpForm
from tasks.models import User
from tasks.tests.helpers import LogInTester
from django.core import mail

class SignUpViewTestCase(TestCase, LogInTester):
    """Tests of the sign up view."""

    fixtures = ['tasks/tests/fixtures/default_user.json']

    def setUp(self):
        self.url = reverse('sign_up')
        self.form_input = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'username': '@janedoe',
            'email': 'janedoe@example.org',
            'new_password': 'Password123',
            'password_confirmation': 'Password123'
        }
        self.user = User.objects.get(username='@johndoe')

    def test_sign_up_url(self):
        self.assertEqual(self.url,'/sign_up/')

    def test_get_sign_up(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertFalse(form.is_bound)

    def test_get_sign_up_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        response = self.client.get(self.url, follow=True)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')

    def test_unsuccesful_sign_up(self):
        self.form_input['username'] = 'BAD_USERNAME'
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'sign_up.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, SignUpForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())

    def test_succesful_sign_up(self):
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count+1)
        response_url = reverse('dashboard')
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        user = User.objects.get(username='@janedoe')
        self.assertEqual(user.first_name, 'Jane')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'janedoe@example.org')
        is_password_correct = check_password('Password123', user.password)
        self.assertTrue(is_password_correct)
        self.assertTrue(self._is_logged_in())

    def test_post_sign_up_redirects_when_logged_in(self):
        self.client.login(username=self.user.username, password="Password123")
        before_count = User.objects.count()
        response = self.client.post(self.url, self.form_input, follow=True)
        after_count = User.objects.count()
        self.assertEqual(after_count, before_count)
        redirect_url = reverse('dashboard')
        self.assertRedirects(response, redirect_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'dashboard.html')
        
    def test_no_email_sent_on_unsuccessful_sign_up(self):
        self.form_input['email'] = 'invalid_email'  # Making the form invalid
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(len(mail.outbox), 0)  # No emails should be sent
        
    def test_email_sent_on_successful_sign_up(self):
        response = self.client.post(self.url, self.form_input)
        self.assertEqual(len(mail.outbox), 1)  # One email should be sent
        self.assertIn('Activate your account', mail.outbox[0].subject)
        
    def test_account_inactive_after_sign_up(self):
        response = self.client.post(self.url, self.form_input)
        user = User.objects.get(username='@janedoe')
        self.assertFalse(user.is_active)
        
    def test_activation_email_content(self):
        response = self.client.post(self.url, self.form_input)
        email_body = mail.outbox[0].body
        self.assertIn('Activate your account', email_body)
        self.assertIn('localhost:8000', email_body)  # Confirm the presence of the activation link
        
    def test_redirect_to_email_verification_notice(self):
        response = self.client.post(self.url, self.form_input)
        verification_notice_url = reverse('email_verification_notice')
        self.assertRedirects(response, verification_notice_url)
