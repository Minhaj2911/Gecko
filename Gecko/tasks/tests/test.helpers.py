from django.test import TestCase
from django.contrib.auth.models import User
from tasks.views import reverse_with_next, LogInTester, MenuTesterMixin
from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

class TestReverseWithNext(TestCase):

    def test_reverse_with_next(self):
        next_url = '/dashboard/'
        url_name = 'log_in' 
        expected_url = f"/url-for-log_in?next={next_url}"  
        self.assertEqual(reverse_with_next(url_name, next_url), expected_url)

class TestLogInTester(TestCase, LogInTester):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_is_logged_in(self):
        self.client.login(username='testuser', password='12345')
        self.assertTrue(self._is_logged_in())

    def test_is_not_logged_in(self):
        self.client.logout()
        self.assertFalse(self._is_logged_in())

class TestMenuTesterMixin(TestCase, MenuTesterMixin):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_assert_menu(self):
        response = self.client.get('/dashboard/')  
        self.assert_menu(response)

    def test_assert_no_menu(self):
        response = self.client.get('/home/')  
        self.assert_no_menu(response)

class LoginProhibitedDecoratorTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_view_redirects_when_logged_in(self):
        # Log in the user
        self.client.login(username='testuser', password='12345')

        # Call the view
        response = self.client.get(reverse('sample_view'))

        # Check that the response is a redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, settings.REDIRECT_URL_WHEN_LOGGED_IN)

    def test_view_loads_when_not_logged_in(self):
        # Call the view without logging in
        response = self.client.get(reverse('sample_view'))

        # Check that the view loads normally
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a sample view.")


