from django.http import HttpResponse
from django.test import TestCase
from django.contrib.auth.models import User
from tasks.helpers import login_prohibited
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
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.authenticated_url = reverse('dashboard') 
        self.non_authenticated_url = reverse('home')  
    @login_prohibited
    def some_view(request):
        return HttpResponse("This is a test view.")

    def test_redirect_authenticated_user(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(self.authenticated_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, settings.REDIRECT_URL_WHEN_LOGGED_IN)

    def test_allow_non_authenticated_user(self):
        response = self.client.get(self.non_authenticated_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "This is a test view.")


