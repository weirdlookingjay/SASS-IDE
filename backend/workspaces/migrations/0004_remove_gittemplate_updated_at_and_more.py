# Generated by Django 5.1.7 on 2025-03-29 16:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspaces', '0003_alter_gittemplate_name_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gittemplate',
            name='updated_at',
        ),
        migrations.RemoveField(
            model_name='resourceclass',
            name='updated_at',
        ),
        migrations.AddField(
            model_name='workspace',
            name='container_password',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='workspace',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workspaces', to=settings.AUTH_USER_MODEL),
        ),
    ]
