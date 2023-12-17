from django.core.management.base import BaseCommand, CommandError

from tasks.models import User, Task

import pytz
from faker import Faker
from random import randint, random
from datetime import timedelta, datetime
from django.utils import timezone
import random

user_fixtures = [
    {'username': '@johndoe', 'email': 'john.doe@example.org', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': '@janedoe', 'email': 'jane.doe@example.org', 'first_name': 'Jane', 'last_name': 'Doe'},
    {'username': '@charlie', 'email': 'charlie.johnson@example.org', 'first_name': 'Charlie', 'last_name': 'Johnson'},
]

task_fixtures = [
    {'title': 'Review client notes', 'description': 'Assess and evaluate current project state based on the client notes', 'assignee': '@johndoe', 'due_date': timezone.now() + timezone.timedelta(days= 3) , 'status': 'in progress'},
    {'title': 'Initiate project plan', 'description': 'Brainstorm new project ideas for banking project', 'assignee': '@janedoe', 'due_date': timezone.now() + timezone.timedelta(days= 10) , 'status': 'completed'},
    {'title': 'Create group schedule', 'description': 'Plan and design a schedule for group weekly meeting', 'assignee': '@charlie', 'due_date': timezone.now() + timezone.timedelta(days= 22) , 'status': 'assigned'},
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 300
    TASK_COUNT = 5
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'
    task_status_options= ['assigned', 'in progress', 'completed']

    def __init__(self):
        self.faker = Faker('en_GB')

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_tasks()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    def create_tasks(self):
        self.generate_task_fixtures()
        self.generate_random_tasks(self.users)
    
    def generate_task_fixtures(self):
        for data in task_fixtures:
            self.try_create_task(data)

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)

    def generate_random_users(self):
        user_count = User.objects.count()
        while  user_count < self.USER_COUNT:
            print(f"Seeding user {user_count}/{self.USER_COUNT}", end='\r')
            self.generate_user()
            user_count = User.objects.count()
        print("User seeding complete.      ")
    
    def generate_random_tasks(self, users):
        task_count = Task.objects.count()
        while  task_count < self.TASK_COUNT:
            print(f"Seeding task {task_count}/{self.TASK_COUNT}", end='\r')
            self.generate_task(users)
            task_count = Task.objects.count()
        print("Task seeding complete.      ")

    def generate_user(self):
        first_name = self.faker.first_name()
        last_name = self.faker.last_name()
        email = create_email(first_name, last_name)
        username = create_username(first_name, last_name)
        self.try_create_user({'username': username, 'email': email, 'first_name': first_name, 'last_name': last_name})
    
    def generate_task(self, users):
        title = self.create_title()
        description = self.faker.text(max_nb_chars=400)
        assignee = random.choice(users)
        due_date = timezone.now() + timezone.timedelta(days= random.randint(1,365))
        status = random.choice(self.task_status_options)
        self.try_create_task({
            'title': title, 'description': description, 'assignee': assignee, 'due_date': due_date, 'status': status})
    
       
    def try_create_user(self, data):
        try:
            self.create_user(data)
        except:
            pass
    
    def try_create_task(self, data):
        try:
            self.create_task(data)
        except:
            pass

    def create_user(self, data):
        User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=Command.DEFAULT_PASSWORD,
            first_name=data['first_name'],
            last_name=data['last_name'],
        )
    
    def create_task(self, data):
        Task.objects.create(
            title=data['title'],
            description=data['description'],
            assignee=data['assignee'],
            due_date=data['due_date'],
            status=data['status'],
        )
    
    def create_title(self):
        title= ""
        while len(title) < 1:
            title= self.faker.text(max_nb_chars=50)
        return title
    
    


def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'



