# Generated by Django 3.2.9 on 2023-01-13 11:10

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20221014_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='TaskLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.TextField(blank=True, default=None, null=True)),
                ('status', models.SmallIntegerField(choices=[(0, 'CREATED'), (1, 'PENDING'), (2, 'RUNNING'), (3, 'SUCCESS'), (4, 'ERROR'), (5, 'TIMEOUT')], default=0)),
                ('error_json', models.TextField(blank=True, default=None, null=True)),
                ('type', models.SmallIntegerField(choices=[(0, 'SETUP'), (1, 'DEPLOY'), (2, 'CONFIG')], default=0)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('parent_task_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='parent_task', to='api.tasklog')),
                ('previous_task_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='previous_task', to='api.tasklog')),
            ],
        ),
    ]