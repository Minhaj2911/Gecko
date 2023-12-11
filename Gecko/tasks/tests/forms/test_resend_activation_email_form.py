from django.test import TestCase
from tasks.forms import ResendActivationEmailForm

class ResendActivationEmailFormTest(TestCase):

    def test_valid_data(self):
        """ Test form with valid data """
        form = ResendActivationEmailForm(data={'email': 'user@example.com'})
        self.assertTrue(form.is_valid())

    def test_invalid_email(self):
        """ Test form with invalid email """
        form = ResendActivationEmailForm(data={'email': 'invalid-email'})
        self.assertFalse(form.is_valid())

    def test_blank_email(self):
        """ Test form with no email provided """
        form = ResendActivationEmailForm(data={'email': ''})
        self.assertFalse(form.is_valid())

    def test_email_field_label(self):
        """ Test label of email field """
        form = ResendActivationEmailForm()
        self.assertEqual(form.fields['email'].label, 'Your email')
