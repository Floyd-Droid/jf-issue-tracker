"""Test Admin user management and user profile management."""

from django.contrib.auth.models import User, Group
from django.test import TestCase, Client
from django.urls import reverse
from issues.forms import (
    UserForm,
    UserGroupForm,
    ManagePasswordForm
)


class TestManageUser(TestCase):
    """Test Admin's ability to edit user information."""
    fixtures = ['fixture.json']

    def setUp(self):
        test_admin = User.objects.get(username='admin1')
        self.client.force_login(user=test_admin)

    def test_user_management_access(self):
        response = self.client.get(reverse('issues:users-list'))
        self.assertEqual(response.status_code, 200)

        # Any user not a member of group 'Admin' is not allowed access.
        test_manager = User.objects.get(username='manager1')
        self.client.force_login(user=test_manager)
        response = self.client.get(reverse('issues:users-list'))
        self.assertEqual(response.status_code, 403)

        test_dev = User.objects.get(username='dev1')
        self.client.force_login(user=test_dev)
        response = self.client.get(reverse('issues:users-list'))
        self.assertEqual(response.status_code, 403)

        test_submitter = User.objects.get(username='submitter1')
        self.client.force_login(user=test_submitter)
        response = self.client.get(reverse('issues:users-list'))
        self.assertEqual(response.status_code, 403)

    def test_admin_user_create(self):
        get_response = self.client.get(reverse('issues:user-create'))
        self.assertEqual(get_response.status_code, 200)
        post_response1 = self.client.post(
            reverse('issues:user-create'), 
            data={'first_name': 'John', 'last_name': 'Doe', 'username': 'jd', 'email': 'jd@gmail.com', 'select_group': '3'}
        )
        self.assertRedirects(post_response1, reverse('issues:users-list'))
        self.assertTrue(User.objects.filter(first_name='John', last_name='Doe', username='jd', email='jd@gmail.com').exists())

        # Invalid data should re-render the page
        post_response2 = self.client.post(
            reverse('issues:user-create'), 
            data={'first_name': '', 'last_name': '', 'username': 'duckman', 'email': 'jd@gmail.com', 'select_group': ''}
        )
        self.assertEqual(post_response2.status_code, 200)
    
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
        self.assertEqual(User.objects.get(username='submitter1').first_name, 'Alexander')

    def test_admin_password_set(self):
        u = User.objects.get(username='submitter1')
        pw1 = u.password
        get_response = self.client.get(reverse('issues:password-update', kwargs={'username': u.username, 'type': 'admin'}))
        self.assertEqual(get_response.status_code, 200)
        
        post_response = self.client.post(
            reverse('issues:password-update', 
            kwargs={'username': u.username, 'type': 'admin'}), 
            {'password': 'Robocop44', 'confirm_password': 'Robocop44'}
        )
        pw2 = User.objects.get(username="submitter1").password

        self.assertRedirects(post_response, reverse('issues:users-list'))
        self.assertNotEqual(pw1, pw2)

        post_response2 = self.client.post(
            reverse('issues:password-update', 
            kwargs={'username': u.username, 'type': 'admin'}), 
            {'password': 'invalid', 'confirm_password': 'invalider'}
        )
        self.assertEqual(post_response2.status_code, 200)
    
    def test_admin_delete_users(self):
        post_response = self.client.post(
            reverse('issues:users-list'), 
            {'select_user': ['2', '3'], 'action': 'delete_users'}
        )

        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(User.objects.get(id=2).is_active)
        self.assertFalse(User.objects.get(id=3).is_active)
    
    def test_set_user_group(self):
        post_response = self.client.post(
            reverse('issues:users-list'), 
            {'select_user': ['2', '3'], 'select_group': '4', 'action': 'set_group'}
        )
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(User.objects.get(id=2).groups.all()[0], Group.objects.get(id=4))
        self.assertEqual(User.objects.get(id=3).groups.all()[0], Group.objects.get(id=4))


class TestUser(TestCase):
    """Test a user's ability to edit their profile."""
    fixtures = ['fixture.json']

    def setUp(self):
        self.user = User.objects.get(username='submitter1')
        self.client.force_login(user=self.user)

    def test_user_signup(self):
        get_response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(get_response.status_code, 200)

        post_response = self.client.post(
            reverse('accounts:signup'), 
            data={'username': 'DannyBoy', 'password1': 'Test46589', 'password2': 'Test46589'}
        )
        self.assertRedirects(post_response, reverse('issues:my-projects'))
        self.assertTrue(User.objects.filter(username='DannyBoy').exists())
        # Each new user should be placed in group 'Manager' by default.
        self.assertEqual(User.objects.get(username='DannyBoy').groups.all()[0].id, 2)
    
    def test_user_update(self):
        get_response = self.client.get(reverse('issues:user-update', kwargs={'username': self.user.username, 'type': 'std-user'}))
        self.assertEqual(get_response.status_code, 200)

        # Change the first name
        post_response = self.client.post(
            reverse('issues:user-update', 
            kwargs={'username': self.user.username, 'type': 'std-user'}), 
            {'first_name': 'Alexander', 'last_name': 'Murphy', 'username': 'submitter1', 'email': 'robocop@gmail.com', 'select_group': '4'}
        )
        self.assertRedirects(post_response, reverse('issues:my-profile', kwargs={'username': self.user.username}))
        self.assertEqual(User.objects.get(username='submitter1').first_name, 'Alexander')

    def test_password_set(self):
        pw1 = self.user.password
        get_response = self.client.get(reverse('issues:password-update', kwargs={'username': self.user.username, 'type': 'std-user'}))
        self.assertEqual(get_response.status_code, 200)
        
        post_response = self.client.post(
            reverse('issues:password-update', 
            kwargs={'username': self.user.username, 'type': 'std-user'}), 
            data={'password': 'Robocop44', 'confirm_password': 'Robocop44'}
        )
        pw2 = User.objects.get(username="submitter1").password

        self.assertEqual(
            post_response.url, 
            reverse('issues:my-profile', kwargs={'username': self.user.username})
        )
        self.assertNotEqual(pw1, pw2)

        # Invalid form data will re-render the page.
        user2 = User.objects.get(username='dev1')
        self.client.force_login(user=user2)

        post_response2 = self.client.post(
            reverse('issues:password-update', kwargs={'username': user2.username, 'type': 'std-user'}), 
            data={'password': 'invalid', 'confirm_password': 'invalider'}
        )
        self.assertEqual(post_response2.status_code, 200)
    
    def test_delete_user(self):
        post_response = self.client.post(
            reverse('issues:profile-delete', 
            kwargs={'username': self.user.username})
        )
        self.assertRedirects(post_response, reverse('login'))
        self.assertFalse(User.objects.get(username='submitter1').is_active)
