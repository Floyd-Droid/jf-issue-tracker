"""Test a demo user's ability to navigate the site without altering the database."""

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse
from issues.models import (
    Project,
    Issue,
    Comment,
    Reply
)

class TestDemoUser(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.user = User.objects.get(username='DemoUser')
        self.client.force_login(user=self.user)
    
    def test_admin_user_create(self):
        get_response = self.client.get(reverse('issues:user-create'))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse('issues:user-create'), 
            data={'first_name': 'John', 'last_name': 'Doe', 'username': 'jd', 'email': 'jd@gmail.com', 'select_group': '3'}
        )
        self.assertRedirects(post_response, reverse('issues:users-list'))
        self.assertFalse(User.objects.filter(username='jd').exists())
    
    def test_admin_user_update(self):
        name = User.objects.get(username='submitter1').username
        get_response = self.client.get(reverse('issues:user-update', kwargs={'username': name, 'type': 'admin'}))
        self.assertEqual(get_response.status_code, 200)

        # Change the first name
        post_response = self.client.post(
            reverse('issues:user-update', 
            kwargs={'username': name, 'type': 'admin'}), 
            {'first_name': 'Alexander', 'last_name': 'Murphy', 'username': 'submitter1', 'email': 'robocop@gmail.com', 'select_group': '4'}
        )
        self.assertRedirects(post_response, reverse('issues:users-list'))
        self.assertEqual(User.objects.get(username='submitter1').first_name, 'Alex')
    
    def test_admin_password_set(self):
        u = User.objects.get(username='submitter1')
        pw1 = u.password
        
        post_response = self.client.post(
            reverse('issues:password-update', 
            kwargs={'username': u.username, 'type': 'admin'}), 
            {'password': 'Robocop44', 'confirm_password': 'Robocop44'}
        )
        pw2 = User.objects.get(username="submitter1").password

        self.assertRedirects(post_response, reverse('issues:users-list'))
        self.assertEqual(pw1, pw2)
    
    def test_admin_delete_users(self):
        post_response = self.client.post(
            reverse('issues:users-list'), 
            {'select_user': ['2', '3'], 'action': 'delete_users'}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertTrue(User.objects.get(id=2).is_active)
        self.assertTrue(User.objects.get(id=3).is_active)
    
    def test_set_user_group(self):
        post_response = self.client.post(
            reverse('issues:users-list'), 
            {'select_user': ['2', '3'], 'select_group': '4', 'action': 'set_group'}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(User.objects.get(id=2).groups.all()[0], Group.objects.get(id=3))
        self.assertEqual(User.objects.get(id=3).groups.all()[0], Group.objects.get(id=2))


class TestDemoProject(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.user = User.objects.get(username='DemoUser')
        self.client.force_login(user=self.user)
        self.p1 = Project.objects.get(title='Project1')

    def test_create_project(self):
        post_response = self.client.post(
            reverse('issues:project-create'), 
            data={'title': 'New test project', 'description': 'A test that creates a new project.'}
        )
        self.assertRedirects(post_response, reverse('issues:projects-list'))
        self.assertFalse(Project.objects.filter(title='New test project', description='A test that creates a new project.').exists())

    def test_project_delete(self):
        response = self.client.post(reverse('issues:project-delete', kwargs={'slug': self.p1.slug}))
        
        self.assertRedirects(response, reverse('issues:projects-list'))
        self.assertTrue(Project.objects.filter(title=self.p1.title).exists())
    
    def test_project_update(self):
        post_response = self.client.post(
            reverse('issues:project-update', kwargs={'slug': self.p1.slug}), 
            data={'title': 'Updated title', 'description': 'Updated description.'}
        )
        self.assertRedirects(post_response, reverse('issues:project-detail', kwargs={'slug': self.p1.slug}))
        self.assertFalse(Project.objects.filter(title='Updated title', description='Updated description.').exists())
    
    def test_project_assign(self):
        user1, user2 = User.objects.get(username='dev2'), User.objects.get(username='manager2')

        post_response = self.client.post(
            reverse('issues:project-assign', 
            kwargs={'slug': self.p1.slug}), 
            data={'selection': [user1.id, user2.id], 'action': 'assign'}
        )
        self.assertRedirects(post_response, reverse('issues:project-assign', kwargs={'slug': self.p1.slug}))
        self.assertNotIn(user1, self.p1.assigned_users.all())
        self.assertNotIn(user2, self.p1.assigned_users.all())
    
    def test_project_unassign(self):
        user1, user2 = User.objects.get(username='dev1'), User.objects.get(username='manager1')

        post_response = self.client.post(
            reverse('issues:project-assign', 
            kwargs={'slug': self.p1.slug}), 
            data={'selection': [user1.id, user2.id], 'action': 'unassign'}
        )
        self.assertRedirects(post_response, reverse('issues:project-assign', kwargs={'slug': self.p1.slug}))
        self.assertIn(user1, self.p1.assigned_users.all())
        self.assertIn(user2, self.p1.assigned_users.all())


class TestDemoIssue(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.user = User.objects.get(username='DemoUser')
        self.client.force_login(user=self.user)
        self.p1 = Project.objects.get(title='Project1')
        self.issue1 = Issue.objects.get(project=self.p1, num=1)
    
    def test_create_project_issue(self):
        assignee = User.objects.get(username='dev2')
        post_response = self.client.post(
            reverse('issues:project-issue-create', 
            kwargs={'slug': self.p1.slug}),
            data={'title': 'New Test Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''}
        )
        self.assertRedirects(post_response, reverse('issues:project-detail', kwargs={'slug': self.p1.slug}))
        self.assertFalse(Issue.objects.filter(title='New Test Issue', description='A test issue.', assignee=assignee.id, priority=3, status='open', issue_type='bug', tag='test', attachment='').exists())
    
    def test_create_issue(self):
        assignee = User.objects.get(username='dev1')
        post_response = self.client.post(
            reverse('issues:issue-create'),
            data={'title': 'New Test Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'project': self.p1.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''}
        )
        self.assertFalse(Issue.objects.filter(title='New Test Issue', description='A test issue.', assignee=assignee, project=self.p1, priority=3, status='open', issue_type='bug', tag='test', attachment='').exists())
        self.assertRedirects(post_response, reverse('issues:my-issues'))
    
    def test_edit_issue(self):
        assignee = User.objects.get(username='dev1')
        post_response = self.client.post(
            reverse('issues:issue-update', 
            kwargs={'project_slug': self.issue1.project.slug, 'issue_num': self.issue1.num}), 
            data={'title': 'Updated Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'project': self.p1.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''}
        )
        self.assertRedirects(post_response, reverse('issues:issue-detail', kwargs={'project_slug': self.issue1.project.slug, 'issue_num': self.issue1.num}))
        self.assertFalse(Issue.objects.filter(title='Updated Issue', description='A test issue.', assignee=assignee, project=self.p1, priority=3, status='open', issue_type='bug', tag='test', attachment='').exists())
    
    def test_delete_issue(self):
        post_response = self.client.post(reverse('issues:issue-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}))

        self.assertRedirects(post_response, reverse('issues:project-detail', kwargs={'slug': self.p1.slug}))
        self.assertTrue(Issue.objects.filter(project=self.p1, num=1).exists())
    
    def test_issue_assign(self):
        user1 = User.objects.get(id=4)
        user2 = User.objects.get(id=5)
        post_response = self.client.post(
            reverse('issues:issue-assign', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}),
            data={'selection': [user1.id, user2.id], 'action': 'assign'}
        )
        self.assertRedirects(post_response, reverse('issues:issue-assign', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}))
        self.assertNotIn(user1, self.issue1.assigned_users.all())
        self.assertNotIn(user2, self.issue1.assigned_users.all())

    def test_issue_unassign(self):
        user1 = User.objects.get(id=2)
        user2 = User.objects.get(id=3)
        post_response = self.client.post(
            reverse('issues:issue-assign', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}),
            data={'selection': [user1.id, user2.id], 'action': 'unassign'}
        )
        self.assertRedirects(post_response, reverse('issues:issue-assign', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}))
        self.assertIn(user1, self.issue1.assigned_users.all())
        self.assertIn(user2, self.issue1.assigned_users.all())
    

class TestDemoComments(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.user = User.objects.get(username='DemoUser')
        self.client.force_login(user=self.user)
        self.p1 = Project.objects.get(title='Project1')
        self.issue1 = Issue.objects.get(project=self.p1, num=1)

    def test_create_comment(self):
        # Demo will attempt to create a new comment (id=5) for Project1 Issue1.
        post_response = self.client.post(
            reverse('issues:comment-create', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), 
            {'text': 'This is a new comment.'}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(Comment.objects.filter(id=5).exists())

    def test_delete_comment(self):
        post_response = self.client.post(
            reverse('issues:comment-delete', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), 
            {'comment-id': 1}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertTrue(Comment.objects.filter(id=1).exists())
    
    def test_update_comment(self):
        post_response = self.client.post(
            reverse('issues:comment-update', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), 
            {'updated-text': 'This is an updated comment.', 'comment-id': 1}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertNotEqual(Comment.objects.get(id=1).text, 'This is an updated comment.')

    
class TestReplies(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.user = User.objects.get(username='DemoUser')
        self.client.force_login(user=self.user)
        self.p1 = Project.objects.get(title='Project1')
        self.p2 = Project.objects.get(title='Project2')
        self.issue1 = Issue.objects.get(project=self.p1, num=1)
    
    def test_create_reply(self):
        # Demo user will attempt to create a new reply (id=4) for comment id=1. 
        post_response = self.client.post(
            reverse('issues:reply-create', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), 
            {'text': 'This is a new reply.', 'comment-id': 1}
        )

        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(Reply.objects.filter(id=4).exists())
    
    def test_delete_reply(self):
        post_response = self.client.post(
            reverse('issues:reply-delete', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), 
            {'reply-id': 1}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertTrue(Reply.objects.filter(id=1).exists())
    
    def test_update_reply(self):
        post_response = self.client.post(
            reverse('issues:reply-update', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), 
            {'updated-text': 'This is an updated reply.', 'reply-id': 1}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertNotEqual(Reply.objects.get(id=1).text, 'This is an updated reply.')
