from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from issues.models import (
    Project,
    Issue
)
import datetime


class TestIssues(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.test_admin = User.objects.get(username='admin1')
        self.client.force_login(user=self.test_admin)
        self.p1 = Project.objects.get(title='Project1')
        self.issue1 = Issue.objects.get(project=self.p1, num=1)
    
    def test_access(self):
        # Admins can create or edit any issues.
        p2 = Project.objects.get(title='Project2')
        get_response1 = self.client.get(reverse('issues:project-issue-create', kwargs={'slug': p2.slug}))
        self.assertEqual(get_response1.status_code, 200)

        # Project Managers, Developers, and Submitters can't create or edit issues for projects they aren't assigned to.
        manager1 = User.objects.get(username='manager1')
        self.client.force_login(user=manager1)
        get_response1 = self.client.get(reverse('issues:project-issue-create', kwargs={'slug': p2.slug}))
        self.assertEqual(get_response1.status_code, 403)

        dev1 = User.objects.get(username='dev1')
        self.client.force_login(user=dev1)
        get_response1 = self.client.get(reverse('issues:project-issue-create', kwargs={'slug': p2.slug}))
        self.assertEqual(get_response1.status_code, 403)

        sub1 = User.objects.get(username='submitter1')
        p2 = Project.objects.get(title='Project2')
        self.client.force_login(user=sub1)
        get_response2 = self.client.get(reverse('issues:project-issue-create', kwargs={'slug': p2.slug}))
        self.assertEqual(get_response2.status_code, 403)

    def test_create_project_issue(self):
        """Test creation of new issues, and ensure the issue number is incremented appropriately"""
        get_response = self.client.get(reverse('issues:project-issue-create', kwargs={'slug': self.p1.slug}))
        self.assertEqual(get_response.status_code, 200)

        assignee = User.objects.get(username='dev2')
        post_response = self.client.post(
            reverse('issues:project-issue-create', kwargs={'slug': self.p1.slug}),
            data={'title': 'New Test Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''}
        )
        # Project1 already has 2 issues in the fixture, so the new issue should be #3.
        self.assertTrue(Issue.objects.filter(title='New Test Issue', description='A test issue.', assignee=assignee.id, priority=3, status='open', issue_type='bug', tag='test', attachment='').exists())
        self.assertRedirects(post_response, reverse('issues:issue-detail', kwargs={'project_slug': self.p1.slug, 'issue_num': 3}))

        # Ensure that the submitter, assignee, and any project managers are assigned to the new issue.
        issue = Issue.objects.get(project=self.p1.id, num=3)
        manager = User.objects.get(username='manager1')
        self.assertIn(assignee, issue.assigned_users.all())
        self.assertIn(self.test_admin, issue.assigned_users.all())
        self.assertIn(manager, issue.assigned_users.all())

        # Since dev2 is the assignee of the new issue, dev2 should now also be assigned to the project.
        self.assertIn(assignee, self.p1.assigned_users.all())
    
    def test_create_issue(self):
        sub1 = User.objects.get(username='submitter1')
        assignee = User.objects.get(username='dev1')
        self.client.force_login(user=sub1)

        post_response = self.client.post(
            reverse('issues:issue-create'),
            data={'title': 'New Test Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'project': self.p1.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''}
        )
        self.assertTrue(Issue.objects.filter(title='New Test Issue', description='A test issue.', assignee=assignee, project=self.p1, priority=3, status='open', issue_type='bug', tag='test', attachment='').exists())
        self.assertRedirects(post_response, reverse('issues:issue-detail', kwargs={'project_slug': self.p1.slug, 'issue_num': 3}))

        issue = Issue.objects.get(project=self.p1.id, num=3)
        manager = User.objects.get(username='manager1')
        self.assertIn(assignee, issue.assigned_users.all())
        self.assertIn(sub1, issue.assigned_users.all())
        self.assertIn(manager, issue.assigned_users.all())

        
    def test_delete_issue(self):
        post_response = self.client.post(reverse('issues:issue-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}))
        self.assertRedirects(post_response, reverse('issues:project-detail', kwargs={'slug': self.p1.slug}))
        self.assertFalse(Issue.objects.filter(project=self.p1, num=1).exists())
        
    def test_edit_issue(self):
        assignee = User.objects.get(username='dev1')
        post_response = self.client.post(
            reverse('issues:issue-update', 
            kwargs={'project_slug': self.issue1.project.slug, 'issue_num': self.issue1.num}), 
            data={'title': 'Updated Issue', 'description': 'A test issue.', 'assignee': assignee.id, 'project': self.p1.id, 'priority': 3, 'status': 'open', 'issue_type': 'bug', 'tag': 'test', 'attachment': ''}
        )
        self.assertRedirects(post_response, reverse('issues:issue-detail', kwargs={'project_slug': self.issue1.project.slug, 'issue_num': self.issue1.num}))
        self.assertTrue(Issue.objects.filter(title='Updated Issue', description='A test issue.', assignee=assignee, project=self.p1, priority=3, status='open', issue_type='bug', tag='test', attachment='').exists())
    
    def test_issue_assign(self):
        user1 = User.objects.get(id=4)
        user2 = User.objects.get(id=5)
        post_response = self.client.post(
            reverse('issues:issue-assign', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}),
            data={'selection': [user1.id, user2.id], 'action': 'assign'}
        )
        self.assertRedirects(post_response, reverse('issues:issue-assign', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}))
        self.assertIn(user1, self.issue1.assigned_users.all())
        self.assertIn(user2, self.issue1.assigned_users.all())

    def test_issue_unassign(self):
        user1 = User.objects.get(id=2)
        user2 = User.objects.get(id=3)
        post_response = self.client.post(
            reverse('issues:issue-assign', 
            kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}),
            data={'selection': [user1.id, user2.id], 'action': 'unassign'}
        )
        self.assertRedirects(post_response, reverse('issues:issue-assign', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}))
        self.assertNotIn(user1, self.issue1.assigned_users.all())
        self.assertNotIn(user2, self.issue1.assigned_users.all())
