"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('create_task/', views.TaskCreateView.as_view(), name='create_task'),
    path('email-verification-notice/', views.email_verification_notice, name='email_verification_notice'),
    path('activate/<uidb64>/<token>/', views.send_activation_email, name='activation_email'), 
    path('resend_activation_email/', views.ResendActivationEmailView.as_view(), name='resend_activation_email'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('create_team/', views.TeamCreationView.as_view(), name='create_team'),
    path('invite_team_members/<str:team>/', views.InviteTeamMembersView.as_view(), name='invite_team_members'), # idk if <> will work
    path('invites/', views.InvitesView.team_invites, name='invites'),
    path('invites/join_team/<str:team>/', views.InvitesView.join_team, name='join_team'),
    path('invites/reject_invite/<str:team>/', views.InvitesView.reject_invite, name='reject_invite'),
    path('team_tasks/<int:pk>/', views.team_tasks, name='team_tasks'),
    
]
