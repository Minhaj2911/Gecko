from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from tasks.models import User
from django.core import mail
from django.urls import reverse
from django.test import TestCase

class PasswordResetTestCase(TestCase):
    fixtures = ['tasks/tests/fixtures/default_user.json']

    def test_password_reset_request(self):
        response = self.client.post(reverse('password_reset'), {'email': 'johndoe@example.org'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('johndoe@example.org', mail.outbox[0].to)

    def test_password_reset_for_nonexistent_user(self):
        response = self.client.post(reverse('password_reset'), {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_process(self):
        # Send the password reset request
        self.client.post(reverse('password_reset'), {'email': 'johndoe@example.org'})
        self.assertEqual(len(mail.outbox), 1)

        # Extract the URL from the email
        email_body = mail.outbox[0].body
        lines = email_body.splitlines()
        reset_url_line = [line for line in lines if '/reset/' in line][0]
        
        # Extract uidb64 and token from the URL
        path_parts = reset_url_line.split('http://testserver/reset/')[1].strip('/').split('/')
        if len(path_parts) >= 2:
            uidb64 = path_parts[0]
            token = path_parts[1]

            # Post to password reset confirm view
            response = self.client.post(reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}), {
                'new_password1': 'TestPass321',
                'new_password2': 'TestPass321',
            }, follow=True)
            print(response.content.decode())

            self.assertEqual(response.status_code, 200)

            # Verify the password has been changed
            user = User.objects.get(email='johndoe@example.org')
            user.refresh_from_db()  # Refresh user instance
            self.assertTrue(user.check_password('TestPass321'))
        else:
            self.fail("Reset URL format is incorrect or token is missing")




