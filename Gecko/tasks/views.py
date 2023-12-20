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
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, TaskForm, TeamForm, TeamSelectForm, TaskStatusForm, TaskFilterForm
from tasks.helpers import login_prohibited
from tasks.models import Task

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    return render(request, 'dashboard.html', {'user': current_user})

@login_required
class TaskDashboardView(LoginRequiredMixin, View):
    """Display the user's task dashboard."""
    def task_dashboard(request):
        """Display the current user's task dashboard."""

    current_user = request.user
    form = TaskFilterForm(request.GET or None)
    tasks = Task.objects.filter(assignee=current_user)

    search_task = request.GET.get('search_input')
    if search_task:
        tasks = tasks.filter(title__icontains=search_task) | tasks.filter(description__icontains=search_task)

    if form.is_valid():
        if form.cleaned_data['title']:
            tasks = tasks.filter(title__icontains=form.cleaned_data['title'])
        if form.cleaned_data['status']:
            tasks = tasks.filter(status=form.cleaned_data['status'])
        if form.cleaned_data['due_date']:
            tasks = tasks.filter(due_date=form.cleaned_data['due_date'])
        if form.cleaned_data['team']:
            tasks = tasks.filter(team=form.cleaned_data['team'])
        if form.cleaned_data.get('priority'):
            tasks = tasks.filter(priority=form.cleaned_data['priority'])

        sort_by = request.GET.get('sort_by', 'due_date')
        if sort_by in ['title', 'status', 'due_date', 'assignee__username', 'team__name','priority', '-priority']:
            tasks = tasks.order_by(sort_by)

    return render(request, 'task_dashboard.html', {'tasks': tasks, 'form': form})


class TaskDescriptionView(View):
    """Display the task's description."""
    def task_description(request, pk):
        """Display the current task's description."""
        #remove try and except???
        current_user = request.user
        
        try:
            task = Task.objects.get(assignee=current_user, pk=pk)

        except Task.DoesNotExist:
            task = None

        return render(request, 'task_description.html', {'task': task})

class TaskChangeStatusView(View):
    """Change a task's status from the task description."""
    def change_task_status(request, pk):
        """Change a particular task's status from the task description."""
        task = Task.objects.get(pk=pk)

        if request.method == 'POST':
            form = TaskStatusForm(request.POST, instance=task)
            if form.is_valid():
                task.status = form.cleaned_data['status']
                task.save()
                return redirect('task_dashboard')
        else:
            form = TaskStatusForm(instance=task)    

        return render(request, 'change_status.html', {'form': form, 'task': task})

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

        elif 'create_task' in request.POST:
            team_id = request.session.get('selected_team_id')
            task_form = TaskForm(request.POST, team_id=team_id)

            if task_form.is_valid():
                task_form.save()
                return redirect('dashboard')  
        
        return render(request, self.template_name, {'team_form': team_form, 'task_form': task_form})
    
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

    
