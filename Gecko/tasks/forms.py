"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from .models import User, Team, Task
from searchableselect.widgets import SearchableSelect
from django.utils import timezone


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""
        
        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user
    

class TeamForm(forms.ModelForm):
    """ Form enabling a user to create a team """
    class Meta:
        """Form options."""
        model= Team
        fields=['name', 'description','members'] # add team_members
        widgets={
            'description': forms.Textarea()}#,
            #'members' :SearchableSelect(model='User', search_field='name', many=True, limit=10)}

    def save(self):
        super().save(commit=False)
        team = Team.objects.create_team(
            name = self.cleaned_data.get('team_name'),
            team_admin = self.request.user,
            description = self.cleaned_data.get('description'),
            members = self.cleaned_data.get('members')
        )

    # def clean(self):
    #     """Clean the data and geberate error message for invalid team members."""
    #     

class TaskForm(forms.ModelForm):
    """ Form enabling team members to create and assign tasks. """

    class Meta:
        """Form options."""
        model= Task
        fields=['title', 'description','assignee', 'due_date', 'status']
        widgets= {
            'due_date': forms.DateTimeInput(
                format= '%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            )
        }

    def clean(self):
        super().clean()
        due_date = self.cleaned_data.get('due_date')
        if due_date is not None and due_date < timezone.now():
            self.add_error('due_date', 'Due date cannot be in the past')

