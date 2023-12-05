"""Unit tests of the team form."""
from django.test import TestCase
from tasks.models import User, Team
from tasks.forms import TeamForm
from django.utils import timezone
from datetime import timedelta, datetime
from django import forms

class TeamFormTestCase(TestCase):
    """Unit tests of the team form."""

    ##user should be replaced with a team member from a group
    def setUp(self):
        super(TestCase, self).setUp()
        self.user_admin = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )
        self.user_1 = User.objects.create_user(
            '@johndoe1',
            first_name='Johna',
            last_name='Doe',
            email='johndoe1@example.org'
        )
        self.user_2 = User.objects.create_user(
            '@johndoe2',
            first_name='Johnb',
            last_name='Doe',
            email='johndoe2@example.org'
        )
        self.user_3 = User.objects.create_user(
            '@johndoe3',
            first_name='Johnc',
            last_name='Doe',
            email='johndoe3@example.org'
        )


        self.form_input = {
            'name' : 'Gecko',
            'description' : 'Scientific reasearch into Geckos',
            'admin': self.user_admin,
            'members' : [self.user_1, self.user_2, self.user_3]
        }

    def test_valid_team_form(self):
        form= TeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form= TeamForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('members', form.fields)
        
    def test_form_rejects_blank_title(self):
        self.form_input['name']= ''
        form= TeamForm(data= self.form_input)
        self.assertFalse(form.is_valid())

    def test_no_repeats_of_admin_in_members(self):
        self.form_input['members'].append(self.user_admin)
        size_before = len(self.form_input['members'])
        form= TeamForm(data= self.form_input)
        size_after = len(form.data.get('members'))
        if size_before == size_after:
            self.assertTrue(form.is_valid())