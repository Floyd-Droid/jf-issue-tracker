# Generated by Django 3.1.1 on 2020-10-13 00:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0013_auto_20201012_1440'),
    ]

    operations = [
        migrations.RenameField(
            model_name='issueuser',
            old_name='user',
            new_name='assigned_user',
        ),
    ]