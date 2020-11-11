# Generated by Django 3.1.1 on 2020-10-08 16:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0003_remove_project_author'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issue',
            old_name='type',
            new_name='issue_type',
        ),
        migrations.RenameField(
            model_name='projectuser',
            old_name='assigned_user_id',
            new_name='assigned_user',
        ),
        migrations.RenameField(
            model_name='projectuser',
            old_name='project_id',
            new_name='project',
        ),
    ]