from django.http import HttpResponse
from django.test import TestCase
from django.contrib.auth.models import User
from tasks.helpers import login_prohibited
from tasks.views import reverse_with_next, LogInTester, MenuTesterMixin
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
        self.client.login(username='testuser', password='12345')

    def test_login_prohibited(self):
        @login_prohibited
        def test_view(request):
            return HttpResponse('Test View')
        response = test_view(self.client.get('/dashboard/'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)

    def test_login_prohibited_with_next(self):
        @login_prohibited
        def test_view(request):
            return HttpResponse('Test View')
        response = test_view(self.client.get('/dashboard/?next=/home/'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home/')

    def test_login_prohibited_with_next_and_query_params(self):
        @login_prohibited
        def test_view(request):
            return HttpResponse('Test View')
        response = test_view(self.client.get('/dashboard/?next=/home/?test=test'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/home/?test=test')

  
  
  
  


