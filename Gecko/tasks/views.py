from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, TaskForm, TeamForm, TeamSelectForm
from tasks.helpers import login_prohibited
from tasks.models import Team, Task, User
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model


@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

class TaskCreateView(LoginRequiredMixin, View):
    template_name = 'create_task.html'
    
    def get(self, request):
        team_form = TeamSelectForm(user=request.user)
        task_form = TaskForm()
        return render(request, self.template_name, {'team_form': team_form, 'task_form': task_form})

    def post(self, request):
        task_form = TaskForm()
        team_form = TeamSelectForm(user=request.user)
        
        if 'select_team' in request.POST:
            kwargs= {'user': request.user}
            team_form = TeamSelectForm(request.POST, **kwargs)

            if team_form.is_valid():
                team = team_form.cleaned_data['team']
                request.session['selected_team_id']= team.id
                task_form = TaskForm(team_id=team.id)
                return render(request, self.template_name, {'team_form': team_form, 'task_form': task_form, 'team_id': team.id})
            else:
                task_form = TaskForm(team_id=team.id)

        elif 'create_task' in request.POST:
            team_id = request.session.get('selected_team_id')
            task_form = TaskForm(request.POST, team_id=team_id)

            if task_form.is_valid():
                task_form.save()
                messages.add_message(self.request, messages.SUCCESS, "Task Created!")
                return redirect('dashboard')
            else:
                # print(task_form.errors)
                messages.error(request,  "Unsuccessful: Task Not Created! ")
                return render(request, self.template_name, {'team_form': team_form, 'task_form': task_form})
        
        else: 
            messages.error(request, "Please select a Team!")
        
        return render(request, self.template_name, {'team_form': TeamSelectForm(user=request.user), 'task_form': task_form})
    
class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        else:
            messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
            return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups.
    Sends an activation email for email verification."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    
    
class TeamCreationView(LoginRequiredMixin, FormView):
    form_class = TeamForm
    template_name = "create_team.html"

    def form_valid(self, form):
        self.object = form.save(self.request)
        messages.add_message(self.request, messages.SUCCESS, "Team Created!")
        return super().form_valid(form)

    def get_success_url(self):
        """Return redirect URL after successful update."""
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.WARNING , "Unsuccessful: Team Not Created")
        return super().form_invalid(form)

    
