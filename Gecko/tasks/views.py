from email.utils import parsedate_to_datetime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render
from django.views.generic import View, FormView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, TaskForm, TeamForm, TeamSelectForm, TaskFilterForm, AssignNewAdminForm, AddMembersForm, RemoveMembersForm
from tasks.helpers import login_prohibited
from tasks.models import Task, Team

@login_required
def dashboard(request):
    """Display the current user's dashboard."""

    current_user = request.user
    user_teams = Team.objects.filter(admin=request.user).distinct() | Team.objects.filter(members=request.user).distinct()
    context = {
        'user': current_user,
        'teams': user_teams
    }

    return render(request, 'dashboard.html', context)

class TeamCreateView(LoginRequiredMixin, FormView): 
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
    


def transfer_admin(request, pk):
    team = Team.objects.get(pk=pk)

    if request.method == 'POST':
        form = AssignNewAdminForm(request.POST, team_members=team.members.exclude(id=request.user.id))
        if form.is_valid():
            new_admin = form.cleaned_data['new_admin']
            team.admin = new_admin
            team.save()
            return redirect('team_detail', team_id=pk)
    else:
        form = AssignNewAdminForm(team_members=team.members.exclude(id=request.user.id))

    return render(request, 'assign_new_admin.html', {'form': form, 'team': team})

def add_members(request, pk):
    team = Team.objects.get(pk=pk)

    if request.user != team.admin:
        return redirect('team_detail')

    existing_member_ids = team.members.values_list('id', flat=True)
    if request.method == 'POST':
        form = AddMembersForm(request.POST, team_members=existing_member_ids)
        if form.is_valid():
            new_members = form.cleaned_data['new_members']
            team.members.add(*new_members)
            return redirect('team_detail', team_id=pk)
    else:
        form = AddMembersForm(team_members=existing_member_ids)

    return render(request, 'add_members.html', {'form': form, 'team': team})

def remove_members(request, pk):
    team = Team.objects.get(pk=pk)

    if request.user != team.admin:
        return redirect('team_detail')

    if request.method == 'POST':
        form = RemoveMembersForm(request.POST, team_members=team.members.all())
        if form.is_valid():
            members_to_remove = form.cleaned_data['members_to_remove']
            for member in members_to_remove:
                team.members.remove(member)
            return redirect('team_detail', team_id=pk)
    else:
        form = RemoveMembersForm(team_members=team.members.all())

    return render(request, 'remove_members.html', {'form': form, 'team': team})

def leave_team(request, pk):
    team = Team.objects.get(pk=pk)
    
    if request.method == 'POST':
        if request.user == team.admin:
            form = AssignNewAdminForm(request.POST, team_members=team.members.exclude(id=request.user.id))
            if form.is_valid():
                new_admin = form.cleaned_data['new_admin']
                team.admin = new_admin
                team.save()
                team.members.remove(request.user)
                return redirect('dashboard')  
            else:
                return render(request, 'assign_new_admin.html', {'form': form, 'team': team})
        else:
            team.members.remove(request.user)
            return redirect('dashboard')  
    if request.user == team.admin:
        form = AssignNewAdminForm(team_members=team.members.exclude(id=request.user.id))
        return render(request, 'assign_new_admin.html', {'form': form, 'team': team})
    else:
        return redirect('dashboard')
    
def delete_team(request, pk):
    team = Team.objects.get(pk=pk)

    if request.user != team.admin:  
        return redirect('team_detail')

    if request.method == 'POST':
        team.delete()
        messages.success(request, 'Team deleted successfully.')
        return redirect('team_detail')

    return redirect('team_detail')

class TeamDashboardView(LoginRequiredMixin, View):
    """Display the current user's team dashboard"""
    
    def dashboard(request):
        """Display the current user's team dashboard."""
        current_user = request.user
        user_teams = Team.objects.filter(members=current_user)
        return render(request, 'dashboard.html', {'user_teams': user_teams})
    

def team_detail(request, pk):
        """Display the current team's tasks."""
        team = Team.objects.get(pk=pk)
        tasks = Task.objects.filter(team_of_task = team)
        is_admin = team.admin == request.user

        context = {
        'team': team,
        'tasks': tasks,
        'is_admin': is_admin,
        }
        return render(request, 'team_detail.html', context)
    
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
                task = task_form.save(commit=False)
                task.team_of_task = Team.objects.get(id=team_id)
                task_form.save()
                return redirect('dashboard')  
        
        return render(request, self.template_name, {'team_form': team_form, 'task_form': task_form})

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
        if sort_by in ['title', 'status', 'due_date', 'assignee__username', 'priority', '-priority', 'team__name']:
            tasks = tasks.order_by(sort_by)

    return render(request, 'task_dashboard.html', {'tasks': tasks, 'form': form})


def task_description(request, pk):
    """Display the current task's description."""

    try:
        task = Task.objects.get(pk=pk)

    except Task.DoesNotExist:
        task = None

    return render(request, 'task_description.html', {'task': task})

class TaskEditView(UpdateView):
    model = Task
    fields = ['title', 'description', 'assignee', 'due_date', 'status', 'priority', 'team']
    template_name = 'task_edit.html'
    form_class = TaskForm

    def get_object(request, pk):
        """Return the object (task) to be updated."""
        task = Task.objects.get(pk=pk)
        return task

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Task updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

def update_task(request, pk):
    task = Task.objects.get(pk=pk)

    if request.method == 'POST':
        action = request.POST.get('action')
        user = request.user

        if action == 'update_status':
            task.status = request.POST.get('status')
        elif action == 'update_priority':
            task.priority = request.POST.get('priority')
        elif action == 'update_assignee':
            user_id = request.POST.get('assignee')
            task.assignee = user.objects.get(id=user_id)
        elif action == 'update_due_date':
            due_date = parsedate_to_datetime(request.POST.get('due_date'))
            task.due_date = due_date

        task.save()
        return redirect('dashboard')

    return redirect('dashboard')


class TaskDeleteView(DeleteView):
    model = Task
    success_url = reverse_lazy('dashboard') 


@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

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
    
    


    
