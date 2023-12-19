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
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm, TaskForm, TeamForm, TeamSelectForm, TaskStatusForm
from tasks.helpers import login_prohibited
from tasks.models import Team, Task, User
from .tokens import account_activation_token
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from .forms import ResendActivationEmailForm
from .models import Task

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
        search_task= request.GET.get('search_input')

        if search_task:
            user_tasks = Task.objects.filter(assignee = current_user).filter(title__icontains= search_task) | Task.objects.filter(assignee = current_user).filter(description__icontains= search_task)

        else:
            user_tasks= Task.objects.filter(assignee = current_user)

        return render(request, 'task_dashboard.html', {'user_tasks': user_tasks, 'user': current_user})

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
        """
        Handle the login attempt. If successful, redirect the user.
        If the user is not active, prompt for email verification.
        """
        
        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user and user.is_active:
            login(request, user)
            return redirect(self.next)
        elif user and not user.is_active:
            messages.add_message(request, messages.ERROR, "Please verify your email to activate your account.") 
            return self.render()
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
    redirect_when_logged_in_url = 'email_verification_notice'

    def form_valid(self, form):
        """Process the valid sign-up form. 
        Creates a user and sends an activation email."""
        
        self.object = form.save()
        self.object.is_active = False
        self.object.save()
        mail_subject = 'Activate your account.'
        message = render_to_string('activation_email.html', {
            'user': self.object,
            'domain': 'localhost:8000',  # replace with pythonanywhere
            'uid': urlsafe_base64_encode(force_bytes(self.object.pk)),
            'token': account_activation_token.make_token(self.object),
        })
        
        to_email = self.object.email
        from_email = settings.EMAIL_HOST_USER
        send_mail(mail_subject, message, from_email, [to_email], fail_silently=False)
        messages.add_message(self.request, messages.INFO, 'Please confirm your email address to complete the registration.')
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the email verification notice page after successful registration."""
        return reverse('email_verification_notice')
    
def email_verification_notice(request):
    """Display a page to notify the user that an email verification has been sent."""
    return render(request, 'email_verification_notice.html')
    
def send_activation_email(request, uidb64, token):
    """Handle the user account activation request.
    Activates the user's account if the token is valid and the user is not already active."""
    
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if not user.is_active:
            user.is_active = True
            user.save()
            messages.success(request, 'Your account has been activated, please log in.')
            return redirect('log_in')
        else:
            messages.info(request, 'You already activated your account, please log in.')
            return redirect('log_in')
    else:
        messages.error(request, 'The activation link is invalid or has expired. Please request a new activation email.')
        return redirect('resend_activation_email')
    

class ResendActivationEmailView(FormView):
    """Handle requests to resend the activation email.
    Verifies if the user exists and is inactive before sending a new activation email."""
    
    template_name = 'resend_activation_email.html'
    form_class = ResendActivationEmailForm

    def form_valid(self, form):
        """Process a valid form and resend the activation email if the user is inactive."""
        
        email = form.cleaned_data['email']
        User = get_user_model()
        user = User.objects.filter(email=email, is_active=False).first()
        
        if user:
            # Construct and send the activation email
            mail_subject = 'Activate your account.'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': 'localhost:8000',  # Replace with your actual domain when deploying
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            send_mail(mail_subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
            messages.success(self.request, 'If an account exists with this email, we have sent a new activation link.')
            return super().form_valid(form)
        else:
            messages.error(self.request, "No inactive account found with the provided email.")
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse('log_in')
    
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

########

# @login_required
# def remove_member_from_team(request):
    
