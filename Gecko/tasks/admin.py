from django.contrib import admin
from .models import Task, User, Team

# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    list_display = [
        'username', 'first_name', 'last_name', 'email'
        #   ,'get_teams'
    ]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tasks."""

    list_display = [
        'title', 'description', 'assignee', 'due_date'
    ]



@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tasks."""

    list_display = [
        'name', 'description', 'admin' , 'get_members' #, 'members' #error wont allow members as it is a many to many field
    ]
