# Generated by Django 3.1.1 on 2020-10-11 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('issues', '0008_auto_20201010_1519'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(error_messages={'required': 'Please select a project.'}, on_delete=django.db.models.deletion.CASCADE, related_name='issue_project', to='issues.project'),
        ),
    ]
