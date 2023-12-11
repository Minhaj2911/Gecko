from django.test import TestCase
from django.urls import reverse
from django.core import mail
from tasks.models import User
from django.contrib.messages import get_messages

class ResendActivationEmailViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse('resend_activation_email')
        self.user = User.objects.create_user('@inactiveuser', 'inactive@example.com', 'password')
        self.user.is_active = False
        self.user.save()

    def test_resend_activation_email_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'resend_activation_email.html')

    def test_resend_activation_email_success(self):
        response = self.client.post(self.url, {'email': 'inactive@example.com'})
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Activate your account.')
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), 'If an account exists with this email, we have sent a new activation link.')
        self.assertRedirects(response, reverse('log_in'))

    def test_resend_activation_email_failure(self):
        User.objects.filter(email='nonexisting@example.com').delete()
        response = self.client.post(self.url, {'email': 'nonexisting@example.com'})
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "No inactive account found with the provided email.")
        self.assertTemplateUsed(response, 'resend_activation_email.html')

    def test_resend_activation_email_invalid_form(self):
        response = self.client.post(self.url, {'email': 'invalid-email'})
        self.assertFormError(response, 'form', 'email', ['Enter a valid email address.'])
