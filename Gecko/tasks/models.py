from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
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
    
class Task(models.Model):
    """" Tasks can be created by team members.  """

    title= models.CharField(max_length=50, blank=False)
    description= models.CharField(max_length=400, blank=True)
    assignee= models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
    )
    due_date= models.DateTimeField()
    
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='assigned')
    #remove lines related to existing_task before merging
    def __init__(self, *args: any, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_task = False

    def clean(self):
        super().clean()
        if not self.existing_task and self.due_date is not None and self.due_date < timezone.now():
            raise ValidationError("Due date cannot be in the past")
        


         




