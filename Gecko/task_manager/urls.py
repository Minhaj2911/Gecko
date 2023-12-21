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
    path('dashboard/', views.TeamDashboardView.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('create_task/', views.TaskCreateView.as_view(), name='create_task'),
    path('create_team/', views.TeamCreateView.as_view(), name='create_team'),
    path('task_dashboard/', views.task_dashboard, name='task_dashboard'),
    path('task_description/<int:pk>', views.task_description, name='task_description'),
    path('update_task/<int:pk>/', views.update_task, name='update_task'),
    path('task/<int:pk>/delete/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('team/<int:team_id>/', views.team_detail, name='team_detail'),
    path('team/<int:team_id>/leave/', views.leave_team, name='leave_team'),
    path('team/<int:team_id>/transfer_admin/', views.transfer_admin, name='transfer_admin'),
    path('team/<int:team_id>/add_members/', views.add_members, name='add_members'),
    path('team/<int:team_id>/remove_members/', views.remove_members, name='remove_members'),
    path('team/<int:team_id>/delete/', views.delete_team, name='delete_team'),
    path('team_tasks/<int:pk>/', views.team_detail, name='team_tasks'),
    path('invites/', views.InvitesView.team_invites, name='invites'),
]
