from typing import Any
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from libgravatar import Gravatar
from django.utils import timezone
from django.core.exceptions import ValidationError

class User(AbstractUser):
    """Model used for user authentication, and team member related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    teams = models.ManyToManyField('Team', related_name='teams', blank=True )

    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""
        
        return self.gravatar(size=60)
    
    def get_teams(self):
        return ",".join([str(m) for m in self.teams.all()]) 

    
class Task(models.Model):
    """" Tasks can be created by team members.  """

    title= models.CharField(max_length=50, blank=False, unique=True)
    description= models.CharField(max_length=400, blank=True)
    due_date= models.DateTimeField()

    assignee= models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        blank= False,
        null= False,
    )
    
    team_of_task= models.ForeignKey(
        "Team",
        on_delete=models.CASCADE,
        null= False,
        blank= False,
        related_name='team_of_task'
        )
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='assigned')

    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
    ]
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=2)

    def __init__(self, *args: Any, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_task= False
    
    def clean(self):
        super().clean()
        if not self.existing_task and self.due_date is not None and self.due_date < timezone.now():
            raise ValidationError("Due date cannot be in the past")

class Team(models.Model):
    """Teams can be created by a user"""
    name = models.CharField(max_length=50, blank=False, unique=True)
    description = models.CharField(max_length=500, blank=True)
    admin = models.ForeignKey(
            "User",
            on_delete=models.CASCADE,
            blank = False
        )
    members = models.ManyToManyField(User, related_name='members',blank = False)

    def get_members(self):
        return ",".join([str(m) for m in self.members.all()]) 
   
    def set_admin(self,user):
        self.admin = user
        
    def clean(self):
        super().clean()
    
    def __str__(self):
        return self.name

