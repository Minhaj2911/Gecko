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
        self.user = User.objects.create_user(
            '@johndoe',
            first_name='John',
            last_name='Doe',
            email='johndoe@example.org'
        )
        self.form_input = {
            team_name= 'Gecko',
            description= 'Scientific reasearch into Geckos',
            team_admin= self.user
            #team members=
        }

    def test_valid_team_form(self):
        form= TeamForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_has_necessary_fields(self):
        form= TeamForm()
        self.assertIn('team_name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('team_admin', form.fields)
        
    def test_form_rejects_blank_title(self):
        self.form_input['team_name']= ''
        form= TeamForm(data= self.form_input)
        self.assertFalse(form.is_valid())