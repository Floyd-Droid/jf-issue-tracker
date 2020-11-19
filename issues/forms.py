from django import forms
from django.contrib.auth.models import User, Group
from .models import (
    Project,
    Issue,
    Comment,
    Reply
)

import re


class UserGroupForm(forms.Form):

    def __init__(self, data=None, *args, **kwargs):
        super(UserGroupForm, self).__init__(data=data, *args, **kwargs)
        
        self.action = data.get('action') if data else None
        if self.action == 'set_group':
            self.fields['select_group'].required = True

    select_user = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(is_active=True),
        widget=forms.SelectMultiple(attrs={'size':'15'})
    )
    select_group = forms.ModelChoiceField(queryset=Group.objects.all(), required=False, empty_label=None)
    

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
        )

    email = forms.EmailField(required=True)
    select_group = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None)

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        email_input = cleaned_data.get('email')
        if 'email' in self.changed_data and User.objects.filter(email=email_input).exists():
            self.add_error('email', 'That email address is already in use.')
        
        return cleaned_data


class ManagePasswordForm(forms.Form):

    password = forms.CharField(
        required=True,
        label='Password', 
        widget=forms.PasswordInput(),
        help_text='Must be at least 8 characters with at least 1 digit and 1 uppercase character.'
    )

    confirm_password = forms.CharField(
        required=True,
        label='Confirm Password', 
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super(ManagePasswordForm, self).clean()
        pw = cleaned_data.get('password')
        confirm_pw = cleaned_data.get('confirm_password')

        if len(pw) < 8:
            self.add_error('confirm_password', 'Password must contain at least 8 characters.')
        if not re.search(r"[\d]+", pw) or not re.search(r"[A-Z]", pw):
            self.add_error('confirm_password', 'Password must contain at least 1 digit and 1 uppercase character.')
        if pw != confirm_pw:
            self.add_error('confirm_password', 'Passwords do not match.')

        return cleaned_data


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = (
            'title',
            'description',
        )
    
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs = {'cols':'60', 'rows':'10'}


class ProjectIssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = (
            'date_created',
            'date_updated',
            'date_closed',
            'submitter',
            'num',
            'assigned_users',
            'project'
        )

    def __init__(self, *args, **kwargs):
        super(ProjectIssueForm, self).__init__(*args, **kwargs)
        self.fields['assignee'].queryset = User.objects.filter(is_active=True)
        self.fields['description'].widget.attrs = {'cols':'60', 'rows':'10'}


class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        exclude = (
            'date_created',
            'date_updated',
            'date_closed',
            'submitter',
            'num',
            'assigned_users',
        )

    def __init__(self, user=None, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)
        # The user should only be able to create issues for projects they are assigned.
        if user:
            self.fields['project'].queryset = user.assigned_projects.all()
        self.fields['assignee'].queryset = User.objects.filter(is_active=True)
        self.fields['description'].widget.attrs = {'cols':'60', 'rows':'10'}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = (
            'text',
        )
    
    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {'cols':'70', 'rows':'10','placeholder':'Leave a comment'}


class ReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = (
            'text',
        )

    def __init__(self, *args, **kwargs):
        super(ReplyForm, self).__init__(*args, **kwargs)
        self.fields['text'].widget.attrs = {'cols':'70', 'rows':'10','placeholder':'Leave a reply'}
