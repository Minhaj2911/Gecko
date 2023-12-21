from django.core.management.base import BaseCommand, CommandError

from tasks.models import User, Task, Team

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
    {'title': 'Review client notes', 'description': 'Assess and evaluate current project state based on the client notes', 'assignee': '@johndoe', 'due_date': timezone.now() + timezone.timedelta(days= 3) , 'status': 'in progress', 'priority': 2, 'team': 'Koala team'},
    {'title': 'Initiate project plan', 'description': 'Brainstorm new project ideas for banking project', 'assignee': '@janedoe', 'due_date': timezone.now() + timezone.timedelta(days= 10) , 'status': 'completed', 'priority': 1, 'team': 'Panda team'},
    {'title': 'Create group schedule', 'description': 'Plan and design a schedule for group weekly meeting', 'assignee': '@charlie', 'due_date': timezone.now() + timezone.timedelta(days= 22) , 'status': 'assigned', 'priority': 3, 'team': 'Kangaroo team'},
]

team_fixtures = [
    {'name': 'Koala team', 'description': 'IT team', 'admin': '@johndoe'},
    {'name': 'Panda team', 'description': 'Design team', 'admin': '@janedoe'},
    {'name': 'Kangaroo team', 'description': 'Plan and analysis team', 'admin': '@charlie' }
]


class Command(BaseCommand):
    """Build automation command to seed the database."""

    USER_COUNT = 10
    TASK_COUNT = 5
    TEAM_COUNT = 10
    MAX_TEAM_MEMBERS = 8
    MAX_TASKS_PER_TEAM = 10
    DEFAULT_PASSWORD = 'Password123'
    help = 'Seeds the database with sample data'
    task_status_options= ['assigned', 'in progress', 'completed']
    # task_priority_options= [1, 2, 3]

    def __init__(self):
        self.faker = Faker('en_GB')
    
    

    def handle(self, *args, **options):
        self.create_users()
        self.users = User.objects.all()
        self.create_tasks()
        self.create_teams()

    def create_users(self):
        self.generate_user_fixtures()
        self.generate_random_users()
    
    def create_tasks(self):
        self.generate_task_fixtures()
        self.generate_random_tasks(self.users)
    
    def create_teams(self):
        self.generate_team_fixtures()
        self.generate_random_teams()

    def generate_user_fixtures(self):
        for data in user_fixtures:
            self.try_create_user(data)
    
    def generate_task_fixtures(self):
        for data in task_fixtures:
            self.try_create_task(data)
    
    def generate_team_fixtures(self):
        for data in team_fixtures:
            self.try_create_team(data)

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

    def generate_random_teams(self):
        team_count = Team.objects.count()
        while  team_count < self.TEAM_COUNT:
            print(f"Seeding team {team_count}/{self.TEAM_COUNT}", end='\r')
            self.generate_team()
            team_count = Team.objects.count()
        print("Team seeding complete.      ")

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
        # priority= random.choice(self.task_priority_options)
        # team= random.choice(Team.objects.all())
        self.try_create_task({
            'title': title, 'description': description, 'assignee': assignee, 'due_date': due_date, 'status': status, 'priority': priority, 'team': team})
    
    def generate_team(self):
        name = self.faker.unique.word()
        description = self.faker.text(max_nb_chars=500)
        admin = random.choice(User.objects.all())
        admin_username= admin.username
        self.try_create_team({'name': name, 'description': description, 'admin': admin_username})
    
       
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
    
    def try_create_team(self, data):
        try:
            self.create_team(data)
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
        # team_name = data['team']
        # team = Team.objects.get(name=team_name)
        Task.objects.create(
            title=data['title'],
            description=data['description'],
            assignee=data['assignee'],
            due_date=data['due_date'],
            status=data['status'], 
            # priority=data['priority'],
            # team=team,
        )
    
    
    def create_team(self, data):
        admin_username = data['admin']
        admin_user = User.objects.get(username=admin_username)
        team = Team.objects.create(
                name=data['name'],
                description=data['description'],
                admin=admin_user,
            )
        team.members.add(admin_user)
        self.add_team_members(team, admin_user)
        # self.add_tasks_for_teams(team)
        
    def add_team_members(self, team, admin_username):
        non_admin_users= User.objects.exclude(username= admin_username)
        for user in non_admin_users[:self.MAX_TEAM_MEMBERS - 1]:
            team.members.add(user)
        
    # def add_tasks_for_teams(self, team):
    #     tasks= Task.objects.all[:self.MAX_TASKS_PER_TEAM]
    #     for task in tasks:
    #         team.tasks.add(task)
    
    
    def create_title(self):
        title= ""
        while len(title) < 1:
            title= self.faker.text(max_nb_chars=50)
        return title
    

def create_username(first_name, last_name):
    return '@' + first_name.lower() + last_name.lower()

def create_email(first_name, last_name):
    return first_name + '.' + last_name + '@example.org'



