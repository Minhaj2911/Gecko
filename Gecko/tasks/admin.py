from django.contrib import admin
from .models import Task, User, Team

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'username', 'first_name', 'last_name', 'email','get_teams','get_invites'
        #   ,'get_teams', 'get_tasks'
    ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tasks."""

    list_display = [
        'title', 'description', 'assignee', 'due_date','team_of_task'
    ]



@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tasks."""

    list_display = [
        'name', 'description', 'admin' , 'get_members','get_tasks' #, 'members' #error wont allow members as it is a many to many field
    ]
