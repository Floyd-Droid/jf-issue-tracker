from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from issues.models import (
    Project,
    Issue,
    Comment,
    Reply
)

class TestComments(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.test_admin = User.objects.get(username='admin1')
        self.client.force_login(user=self.test_admin)
        self.p1 = Project.objects.get(title='Project1')
        self.p2 = Project.objects.get(title='Project2')
        self.issue1 = Issue.objects.get(project=self.p1, num=1)

    def test_admin_edit(self):
        # Admins can delete or edit any comment, whether or not assigned to a project.
        post_response1 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 1})
        self.assertEqual(post_response1.status_code, 200)

        # 'admin1' is not assigned to Project2.
        post_response2 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p2.slug, 'issue_num': self.issue1.num}), {'comment-id': 2})
        self.assertEqual(post_response2.status_code, 200)
    
    def test_manager_edit(self):
        # Project Managers can delete or edit any comment only on projects/issues they are assigned.
        manager1 = User.objects.get(username='manager1')
        self.client.force_login(user=manager1)
        post_response1 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 1})
        self.assertEqual(post_response1.status_code, 200)

        # 'manager1' is not assigned to Project2
        post_response2 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p2.slug, 'issue_num': self.issue1.num}), {'comment-id': 2})
        self.assertEqual(post_response2.status_code, 403)
    
    def test_developer_edit(self):
        # Developers can only delete or edit comments they have authored.
        # 'dev1' has authored comment id=2
        dev1 = User.objects.get(username='dev1')
        self.client.force_login(user=dev1)
        post_response1 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 1})
        self.assertEqual(post_response1.status_code, 403)

        post_response2 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 2})
        self.assertEqual(post_response2.status_code, 200)
    
    def test_submitter_edit(self):
        # Submitters can only delete or edit comments they have authored.
        # 'submitter1' has authored comment id=3
        sub1 = User.objects.get(username='submitter1')
        self.client.force_login(user=sub1)
        post_response1 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 1})
        self.assertEqual(post_response1.status_code, 403)

        post_response2 = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 3})
        self.assertEqual(post_response2.status_code, 200)

    def test_create_comment(self):
        # A new comment (id=5) will be created for Project1 Issue1.
        post_response = self.client.post(reverse('issues:comment-create', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'text': 'This is a new comment.'})

        self.assertEqual(post_response.status_code, 200)
        new_comment = Comment.objects.get(id=5)
        self.assertEqual(new_comment.text, 'This is a new comment.')
        self.assertEqual(new_comment.author, self.test_admin)
        self.assertEqual(new_comment.issue, self.issue1)

        # The author should be the current user.
        new_comment = Comment.objects.get(text='This is a new comment.', issue=self.issue1)
        self.assertEqual(new_comment.author, self.test_admin)
    
    def test_comment_delete(self):
        # Project1 Issue1 has a comment with id=1.
        post_response = self.client.post(reverse('issues:comment-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'comment-id': 1})

        self.assertEqual(post_response.status_code, 200)

        # The comment won't actually be deleted. Instead, the text attr is replaced with "[deleted]".
        self.assertEqual(Comment.objects.get(id=1).text, '[deleted]')
    
    def test_update_comment(self):
        post_response = self.client.post(reverse('issues:comment-update', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'updated-text': 'This is an updated comment.', 'comment-id': 1})

        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(Comment.objects.get(id=1).text, 'This is an updated comment.')


class TestReplies(TestCase):
    fixtures = ['fixture.json']

    def setUp(self):
        self.test_admin = User.objects.get(username='admin1')
        self.client.force_login(user=self.test_admin)
        self.p1 = Project.objects.get(title='Project1')
        self.p2 = Project.objects.get(title='Project2')
        self.issue1 = Issue.objects.get(project=self.p1, num=1)
    
    def test_admin_edit(self):
        # Admins can delete or edit any reply, whether or not assigned to a project.
        post_response1 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 1})
        self.assertEqual(post_response1.status_code, 200)

        # 'admin1' is not assigned to Project2 (first reply is id=3)
        post_response2 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p2.slug, 'issue_num': self.issue1.num}), {'reply-id': 3})
        self.assertEqual(post_response2.status_code, 200)
    
    def test_manager_edit(self):
        # Project Managers can delete or edit any reply only on projects/issues they are assigned.
        manager1 = User.objects.get(username='manager1')
        self.client.force_login(user=manager1)
        post_response1 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 1})
        self.assertEqual(post_response1.status_code, 200)

        # 'manager1' is not assigned to Project2 (first reply is id=3)
        post_response2 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p2.slug, 'issue_num': self.issue1.num}), {'reply-id': 3})
        self.assertEqual(post_response2.status_code, 403)
    
    def test_developer_edit(self):
        # Developers can only delete or edit replies they have authored.
        # 'dev1' has authored reply id=1
        dev1 = User.objects.get(username='dev1')
        self.client.force_login(user=dev1)
        post_response1 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 1})
        self.assertEqual(post_response1.status_code, 200)

        post_response2 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 2})
        self.assertEqual(post_response2.status_code, 403)
    
    def test_submitter_edit(self):
        # Submitters can only delete or edit replies they have authored.
        # 'submitter1' has authored reply id=2
        sub1 = User.objects.get(username='submitter1')
        self.client.force_login(user=sub1)
        post_response1 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 1})
        self.assertEqual(post_response1.status_code, 403)

        post_response2 = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 2})
        self.assertEqual(post_response2.status_code, 200)

    def test_create_reply(self):
        # A new reply (id=4) will be created for comment id=1. 
        post_response = self.client.post(reverse('issues:reply-create', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'text': 'This is a new reply.', 'comment-id': 1})

        self.assertEqual(post_response.status_code, 200)
        new_reply = Reply.objects.get(id=4)
        self.assertEqual(new_reply.text, 'This is a new reply.')
        self.assertEqual(new_reply.comment, Comment.objects.get(id=1))
        self.assertEqual(new_reply.author, self.test_admin)
    
    def test_delete_reply(self):
        # Project1 Issue1 Comment1 has a reply with id=1.
        post_response = self.client.post(reverse('issues:reply-delete', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'reply-id': 1})

        self.assertEqual(post_response.status_code, 200)

        # The reply won't actually be deleted. Instead, the text attr is replaced with "[deleted]".
        self.assertEqual(Reply.objects.get(id=1).text, '[deleted]')
    
    def test_update_reply(self):
        post_response = self.client.post(reverse('issues:reply-update', kwargs={'project_slug': self.p1.slug, 'issue_num': self.issue1.num}), {'updated-text': 'This is an updated reply.', 'reply-id': 1})

        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(Reply.objects.get(id=1).text, 'This is an updated reply.')
