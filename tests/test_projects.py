from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from issues.models import (
    Project,
    Issue,
    Comment,
    Reply
)


class TestProjects(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        # Users 'dev1', 'manager1', and 'submitter1' are assigned to Project1.
        # Users 'dev2', 'manager2', and 'submitter2' are assigned to Project2.
        test_admin = User.objects.get(username='admin1')
        self.client.force_login(user=test_admin)
        self.p1 = Project.objects.get(title='Project1')

    def test_manage_project_access(self):
        """Only an admin has access to all projects."""
        response = self.client.get(reverse('issues:projects-list'))
        self.assertEqual(response.status_code, 200)

        # Group 'Project Manager', 'Developer' and 'Submitter' are not allowed access.
        test_manager = User.objects.get(username='manager1')
        self.client.force_login(user=test_manager)
        response = self.client.get(reverse('issues:projects-list'))
        self.assertEqual(response.status_code, 403)

        test_dev = User.objects.get(username='dev1')
        self.client.force_login(user=test_dev)
        response = self.client.get(reverse('issues:projects-list'))
        self.assertEqual(response.status_code, 403)

        test_submitter = User.objects.get(username='submitter1')
        self.client.force_login(user=test_submitter)
        response = self.client.get(reverse('issues:projects-list'))
        self.assertEqual(response.status_code, 403)
    
    def test_project_edit_access(self):
        # Managers can only edit projects they are assigned to.
        p2 = Project.objects.get(title='Project2')

        self.client.force_login(user=User.objects.get(username='manager1'))
        get_response1 = self.client.get(reverse('issues:project-update', kwargs={'slug': self.p1.slug}))
        self.assertEqual(get_response1.status_code, 200)
        post_response1 = self.client.post(reverse('issues:project-delete', kwargs={'slug': self.p1.slug}))
        self.assertEqual(post_response1.status_code, 302)
        get_response2 = self.client.get(reverse('issues:project-update', kwargs={'slug': p2.slug}))
        self.assertEqual(get_response2.status_code, 403)
        post_response2 = self.client.post(reverse('issues:project-delete', kwargs={'slug': p2.slug}))
        self.assertEqual(post_response2.status_code, 403)

    def test_developer_project_edit_access(self):
        # Developers can't edit or delete any projects.
        self.client.force_login(user=User.objects.get(username='dev1'))
        get_response5 = self.client.get(reverse('issues:project-update', kwargs={'slug': self.p1.slug}))
        self.assertEqual(get_response5.status_code, 403)
        post_response5 = self.client.post(reverse('issues:project-delete', kwargs={'slug': self.p1.slug}))
        self.assertEqual(post_response5.status_code, 403)
    
    def test_submitter_project_edit_access(self):
        #Submitters can't edit or delete any projects.
        self.client.force_login(user=User.objects.get(username='submitter1'))
        get_response6 = self.client.get(reverse('issues:project-update', kwargs={'slug': self.p1.slug}))
        self.assertEqual(get_response6.status_code, 403)
        post_response6 = self.client.post(reverse('issues:project-delete', kwargs={'slug': self.p1.slug}))
        self.assertEqual(post_response6.status_code, 403)
    
    def test_project_create(self):
        """Test creation of project, and assign the creator to the project if a manager."""
        manager = User.objects.get(username='manager1')
        self.client.force_login(user=manager)
        get_response = self.client.get(reverse('issues:project-create'))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse('issues:project-create'), 
            data={'title': 'New test project', 'description': 'A test that creates a new project.'})

        new_project = Project.objects.get(title='New test project', description='A test that creates a new project.')
        self.assertRedirects(post_response, reverse('issues:project-detail', kwargs={'slug': new_project.slug}))
        self.assertTrue(Project.objects.filter(title='New test project', description='A test that creates a new project.').exists())
        self.assertIn(manager, new_project.assigned_users.all())

    def test_project_delete(self):
        issues = self.p1.issues.all()
        comments = Comment.objects.filter(issue__in=issues)
        response = self.client.post(reverse('issues:project-delete', kwargs={'slug': self.p1.slug}))
        
        self.assertRedirects(response, reverse('issues:projects-list'))
        self.assertFalse(Project.objects.filter(title=self.p1.title).exists())

        # All issues, Comments, and Replies associated with the project should also be deleted.
        self.assertFalse(Issue.objects.filter(project=self.p1).exists())
        self.assertFalse(Comment.objects.filter(issue__in=issues).exists())
        self.assertFalse(Reply.objects.filter(comment__in=comments).exists())

    def test_project_update(self):
        get_response = self.client.get(reverse('issues:project-update', kwargs={'slug': self.p1.slug}))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse('issues:project-update', 
            kwargs={'slug': self.p1.slug}), 
            data={'title': 'Updated title', 'description': 'Updated description.'}
        )
        self.assertRedirects(post_response, reverse('issues:project-detail', kwargs={'slug': 'updated-title'}))
        self.assertTrue(Project.objects.filter(title='Updated title', description='Updated description.').exists())
    
    def test_project_assign(self):
        user1, user2 = User.objects.get(username='dev2'), User.objects.get(username='manager2')
        get_response = self.client.get(reverse('issues:project-assign', kwargs={'slug': self.p1.slug}))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse('issues:project-assign', 
            kwargs={'slug': self.p1.slug}), 
            data={'selection': [user1.id, user2.id], 'action': 'assign'}
        )
        self.assertRedirects(post_response, reverse('issues:project-assign', kwargs={'slug': self.p1.slug}))
        self.assertIn(user1, self.p1.assigned_users.all())
        self.assertIn(user2, self.p1.assigned_users.all())

        # A manager assigned to a project should also have all project issues assigned to them.
        issues = self.p1.issues.all()
        for issue in issues:
            self.assertNotIn(user1, issue.assigned_users.all())
            self.assertIn(user2, issue.assigned_users.all())

    def test_project_unassign(self):
        user1, user2 = User.objects.get(username='dev1'), User.objects.get(username='manager1')
        post_response = self.client.post(
            reverse('issues:project-assign', 
            kwargs={'slug': self.p1.slug}), 
            data={'selection': [user1.id, user2.id], 'action': 'unassign'}
        )
        self.assertRedirects(post_response, reverse('issues:project-assign', kwargs={'slug': self.p1.slug}))
        self.assertNotIn(user1, self.p1.assigned_users.all())
        self.assertNotIn(user2, self.p1.assigned_users.all())

        issues = self.p1.issues.all()
        for issue in issues:
            self.assertNotIn(user1, issue.assigned_users.all())
            self.assertNotIn(user2, issue.assigned_users.all())
