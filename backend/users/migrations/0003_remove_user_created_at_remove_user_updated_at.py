# Generated by Django 5.1.7 on 2025-03-29 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_is_admin'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='created_at',
        ),
        migrations.RemoveField(
            model_name='user',
            name='updated_at',
        ),
    ]
