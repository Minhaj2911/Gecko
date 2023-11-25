import django.contrib.auth.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ( 'tasks','0001_initial'),# add teams
    ]

    migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date created')),
                ('name', models.CharField(max_length=50)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)), #idk if this works
                ('members', models.ManyToManyField(blank=True, help_text='The Team members in this Team.', related_name='teams', related_query_name='user', to='auth.group', verbose_name='Team Members')),
            ],
        ),