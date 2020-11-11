"""Test each form directly for expected validation behavior."""

from django.contrib.auth.models import User
from django.test import TestCase, Client
from issues.forms import (
    UserForm, 
    UserGroupForm,
    ManagePasswordForm,
    ProjectForm,
    ProjectIssueForm,
    IssueForm,
    CommentForm,
    ReplyForm
)
from issues.models import (
    Project,
    Issue
)
import datetime


class TestManageUserForms(TestCase):
    fixtures = ['fixture.json']
    
    def test_valid_user_form(self):
        valid_form = UserForm(data={'first_name': 'John', 'last_name': 'Doe', 'username': 'jd', 'email': 'jd@gmail.com', 'select_group': 3})
        self.assertTrue(valid_form.is_valid())
    
    def test_invalid_user_form(self):
        invalid_form = UserForm(data={'username': 'admin1', 'email': 'hsimp@gmail.com'})
        self.assertEqual(invalid_form.errors['username'], ['A user with that username already exists.'])
        self.assertEqual(invalid_form.errors['email'], ['That email address is already in use.'])
        self.assertEqual(invalid_form.errors['select_group'], ['This field is required.'])
    
    def test_valid_password_form(self):
        valid_form = ManagePasswordForm(data={'password':'Test4444', 'confirm_password': 'Test4444'})
        self.assertTrue(valid_form.is_valid())
    
    def test_invalid_password_form(self):
        invalid_form = ManagePasswordForm(data={'password':'invalid', 'confirm_password': 'invalider'})
        self.assertIn('Password must contain at least 8 characters.', invalid_form.errors['confirm_password'])
        self.assertIn('Password must contain at least 1 digit and 1 uppercase character.', invalid_form.errors['confirm_password'])
        self.assertIn('Passwords do not match.', invalid_form.errors['confirm_password'])
    
    def test_valid_user_group_form(self):
        valid_form1 = UserGroupForm(data={'select_user': ['2', '3'], 'select_group': '3', 'action': 'set_group'})
        self.assertTrue(valid_form1.is_valid())

        valid_form2 = UserGroupForm(data={'select_user': ['2', '3'], 'select_group': '', 'action': 'delete_users'})
        self.assertTrue(valid_form2.is_valid())
    
    def test_invalid_user_group_form(self):
        invalid_form = UserGroupForm(data={'select_user': [], 'select_group': '', 'action': 'set_group'})
        self.assertIn('This field is required.', invalid_form.errors['select_user'])
        self.assertIn('This field is required.', invalid_form.errors['select_group'])


class TestProjectForm(TestCase):
    fixtures = ['fixture.json']

    def test_valid_project_form(self):
        valid_form = ProjectForm(data={'title': 'Test title', 'description': 'Test description'})
        self.assertTrue(valid_form.is_valid())
    
    def test_invalid_project_form(self):
        invalid_form1 = ProjectForm(data={'title': ''})
        self.assertIn('This field is required.', invalid_form1.errors['title'])

        invalid_form2 = ProjectForm(data={'title': 'Project1', 'description': 'The title already exists.'})
        self.assertIn('A project with this title already exists.', invalid_form2.errors['title'])


class TestProjectIssueForm(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.test_project = Project.objects.get(title='Project1')

    def test_valid_issue_form(self):
        assignee = User.objects.get(username='dev1')
        valid_form = ProjectIssueForm(data={'title': 'New Test Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''})

        self.assertTrue(valid_form.is_valid())
    
    def test_invalid_issue_form(self):
        invalid_form = ProjectIssueForm(data={'title': '', 'description': '', 'assignee': '', 'priority': '', 'status': 'open', 'issue_type': 'bug', 'tag': '', 'attachment': ''})

        self.assertIn('This field is required.', invalid_form.errors['title'])
        self.assertIn('This field is required.', invalid_form.errors['description'])
        self.assertNotIn('assignee', invalid_form.errors)
        self.assertNotIn('tag', invalid_form.errors)
        self.assertNotIn('attachment', invalid_form.errors)
    

class TestIssueForm(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.test_project = Project.objects.get(title='Project1')

    def test_valid_issue_form(self):
        submitter = User.objects.get(username='submitter1')
        assignee = User.objects.get(username='dev1')
        valid_form = IssueForm(user=submitter, data={'title': 'New Test Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'project': self.test_project.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''})

        self.assertTrue(valid_form.is_valid())
    
    def test_invalid_issue_form(self):
        submitter = User.objects.get(username='submitter1')
        invalid_form = IssueForm(user=submitter, data={'title': '', 'description': '', 'assignee': '', 'project': '', 'priority': '', 'status': 'open', 'issue_type': 'bug', 'tag': '', 'attachment': ''})

        self.assertIn('This field is required.', invalid_form.errors['title'])
        self.assertIn('This field is required.', invalid_form.errors['description'])
        self.assertIn('This field is required.', invalid_form.errors['project'])
        self.assertNotIn('assignee', invalid_form.errors)
        self.assertNotIn('tag', invalid_form.errors)
        self.assertNotIn('attachment', invalid_form.errors)


class TestCommentsForm(TestCase):
    
    def test_comment_form(self):
        valid_form = CommentForm(data={'text': 'New comment.'})
        self.assertTrue(valid_form.is_valid())

        invalid_form = CommentForm(data={'text': ''})
        self.assertFalse(invalid_form.is_valid())
        self.assertIn('This field is required.', invalid_form.errors['text'])

    def test_reply_form(self):
        valid_form = ReplyForm(data={'text': 'New comment.', 'comment-id': 1})
        self.assertTrue(valid_form.is_valid())

        invalid_form = ReplyForm(data={'text': ''})
        self.assertFalse(invalid_form.is_valid())
        self.assertIn('This field is required.', invalid_form.errors['text'])
