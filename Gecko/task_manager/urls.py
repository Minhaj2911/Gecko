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
    path('create_team/', views.TeamCreateView.as_view(), name='create_team'),
    path('task_dashboard/', views.task_dashboard, name='task_dashboard'),
    path('task_description/<int:pk>/', views.task_description, name='task_description'),
    path('update_task/<int:pk>/', views.update_task, name='update_task'),
    path('task_edit/<int:pk>/', views.TaskEditView.as_view(), name='task_edit'),
    path('delete_task/<int:pk>/', views.TaskDeleteView.as_view(), name='task_delete'),
    path('leave_team/<int:pk>/', views.leave_team, name='leave_team'),
    path('transfer_admin/<int:pk>/', views.transfer_admin, name='assign_new_admin'),
    path('add_members/<int:pk>/', views.add_members, name='add_members'),
    path('remove_members/<int:pk>/', views.remove_members, name='remove_members'),
    path('delete_team/<int:pk>/', views.delete_team, name='delete_team'),
    path('team_detail/<int:pk>/', views.team_detail, name='team_detail'),
    path('invites/', views.InvitesView.team_invites, name='invites'),
    path('invites/join_team/<str:team>/', views.InvitesView.join_team, name='join_team'),
    path('invites/reject_invite/<str:team>/', views.InvitesView.reject_invite, name='reject_invite'),
]
