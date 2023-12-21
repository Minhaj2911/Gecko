"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Task, Team
from django.core.exceptions import ValidationError
from django.utils import timezone


class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""
        
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_active:
                return user
        return None


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
        fields=['name', 'description', 'members'] 
        widgets={
            'description': forms.Textarea()}
           

    def save(self,request):
        super().save(commit=False)
        team = Team.objects.create(
            name = self.cleaned_data.get('name'),
            admin = request.user,
            description = self.cleaned_data.get('description')
        )
        team.members.add(request.user)

        for member in self.cleaned_data.get('members').all():
            if member != request.user:
                member.invites.add(team)
        
        return team

    def clean(self):
        super().clean()
        """Clean the data and geberate error message for invalid admin."""
        admin = self.cleaned_data.get('admin')
        members = self.cleaned_data.get('members')
        if not members and members == []:
            self.add_error('members', 'members cannot be empty') 

class AddMembersForm(forms.Form):
    new_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(), 
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    def __init__(self, *args, **kwargs):
        team_members = kwargs.pop('team_members')
        super().__init__(*args, **kwargs)
        self.fields['new_members'].queryset = User.objects.exclude(id__in=team_members)

class RemoveMembersForm(forms.Form):
    members_to_remove = forms.ModelMultipleChoiceField(
        queryset=None,  
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Select Members to Remove"
    )

    def __init__(self, *args, **kwargs):
        team_members = kwargs.pop('team_members')
        super().__init__(*args, **kwargs)
        self.fields['members_to_remove'].queryset = team_members
        

class TaskForm(forms.ModelForm):
    """ Form enabling team members to create and assign tasks. """

    class Meta:
        """Form options."""
        model= Task
        fields=['title', 'description', 'assignee', 'due_date', 'status', 'priority', 'team_of_task']
        widgets= {
                'due_date': forms.DateTimeInput(
                format= '%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'}
            )
        }

    def __init__(self, *args, **kwargs):
        user= kwargs.pop('user', None)
        team_id = kwargs.pop('team_id', None)
        super(TaskForm, self).__init__(*args, **kwargs)
        if team_id:
             team = Team.objects.get(id= team_id)
             self.fields['assignee'].queryset = team.members.all()
        elif user:
            teams= user.teams.all()
            members= User.objects.filter(teams__in= teams).distinct()
            self.fields['assignee'].queryset = members

    def clean(self):
        super().clean()
        due_date = self.cleaned_data.get('due_date')

        if due_date is not None and due_date < timezone.now():
            self.add_error('due_date', 'Due date cannot be in the past')

class TeamSelectForm(forms.Form):
    """ Form enabling users to select a team in order to create and assign tasks. """
    team= forms.ModelChoiceField(
        queryset= Team.objects.none(),
        label= "Select Team",
        empty_label=None
    )  

    def __init__(self, *args, **kwargs):
        user= kwargs.pop('user', None)
        super(TeamSelectForm, self).__init__(*args, **kwargs)
        if user:
            self.fields['team'].queryset = Team.objects.filter(members=user)

class AssignNewAdminForm(forms.Form):
    new_admin = forms.ModelChoiceField(queryset=None, label="Select New Admin")

    def __init__(self, *args, **kwargs):
        team_members = kwargs.pop('team_members')
        super().__init__(*args, **kwargs)
        self.fields['new_admin'].queryset = team_members

class TaskFilterForm(forms.Form):
    title = forms.CharField(required=False)
    assignee = forms.ModelChoiceField(queryset=User.objects.all(), required=False)
    due_date_start = forms.DateTimeField(required=False)
    due_date_end = forms.DateTimeField(required=False)
    status = forms.ChoiceField(choices=Task.STATUS_CHOICES, required=False)
    team = forms.ModelChoiceField(queryset=Team.objects.all(), required=False)
    priority = forms.ChoiceField(choices=Task.PRIORITY_CHOICES, required=False)

