from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import View 
from django.views.generic import (
    DetailView, 
    FormView,
    CreateView,
    DeleteView,
    UpdateView,
    ListView
)

from .forms import (
    UserGroupForm,
    UserForm,
    ManagePasswordForm,
    ProjectForm,
    ProjectIssueForm,
    IssueForm,
    CommentForm,
    ReplyForm
)
from .models import (
    Project,
    Issue,
    Comment,
    Reply
)

import datetime

def get_users_str(username_list):
    """Return a string of comma-separated user names for success messages."""
    users_str = username_list[0]
    for i in range(1, len(username_list)):
        users_str += f", {username_list[i]}"
    return users_str


class DemoLoginView(View):
    """Log user in as DemoUser and display message."""
    def get(self, request, *args, **kwargs):
        user = User.objects.get(username='DemoUser', email='demo@ex.com')
        login(request, user=user)
        messages.success(self.request, f"You are currently logged in as a demo user. This means that you can interact with this website as if you are an admin, but any attempted changes will not actually be saved.")
        return redirect(reverse('issues:my-issues'))


class ManageUsersView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'issues/users_list.html'
    # User table info is sometimes not completely up to date for some reason;
    # Refresh from db to ensure accurate info is displayed.
    User.refresh_from_db # TODO - doesn't seem to always work.
    users = User.objects.filter(is_active=True)
    form_class = UserGroupForm
    context = {
        'users': users,
        'form': form_class,
        'user_type': 'admin'
    }

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.context)
    
    def form_valid(self, form):
        user_obj_set = form.cleaned_data.get('select_user')
        username_list = []
        if self.request.POST.get('action') == 'set_group':
            group_obj = form.cleaned_data.get('select_group')
            group_name = group_obj.name
            
            # Change selected user groups and get list of user names.
            for u in user_obj_set:
                username_list.append(f'{u.username}')
                if self.request.user.email != 'demo@ex.com':
                    u.groups.set([group_obj.id])
                    u.save()
            
            users_str = get_users_str(username_list)
            messages.success(self.request, f"The following users have been successfully added to group "
                f"'{group_name}': {users_str}.")
            self.context['form'] = self.form_class
            return render(self.request, self.template_name, self.context)

        elif self.request.POST.get('action') == 'delete_users':
            for u in user_obj_set:
                username_list.append(f'{u.username}')
                if self.request.user.email != 'demo@ex.com':
                    u.is_active = False
                    u.save()

            users_str = get_users_str(username_list)
            messages.success(self.request, f"The following users are now inactive: {users_str}.")
            self.context['form'] = self.form_class
            return render(self.request, self.template_name, self.context)
    
    def form_invalid(self, form):
        self.context['form'] = form
        return render(self.request, self.template_name, self.context)


class PasswordView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'issues/password_update.html'
    form_class = ManagePasswordForm

    def test_func(self):
        user_type = self.kwargs.get('type')
        if user_type == 'admin':
            return self.request.user.groups.filter(name='Admin').exists()
        elif user_type == 'std-user':
            return True if self.request.user == self.get_user_object() else False

    def get_user_object(self):
        name = self.kwargs.get('username')
        return get_object_or_404(User, username=name)
    
    def get(self, request, *args, **kwargs):
        context = {
            "user_obj": self.get_user_object(),
            "form": self.form_class,
            'user_type': self.kwargs.get('type')
        }
        return render(request, self.template_name, context)
        
    def form_valid(self, form):
        u = self.get_user_object()
        if self.request.user.email != 'demo@ex.com':
            new_pw = form.cleaned_data.get('password')
            u.set_password(new_pw)
            u.save()

        if self.kwargs.get('type') == 'admin':
            messages.success(self.request, f"The password for {u.username} has been successfully updated.")
            return redirect(reverse('issues:users-list'))
        else:
            messages.success(self.request, f"Your password has been updated. Please log in to continue.")
            return redirect(reverse('issues:my-profile', kwargs={'username': self.request.user.username}))

    def form_invalid(self, form):
        context = {
            'form': form,
            'user_obj': self.get_user_object(),
            'user_type': self.kwargs.get('type')
        }
        return render(self.request, self.template_name, context)


class UserCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'issues/user_create_or_update.html'
    form_class = UserForm

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()
    
    def form_valid(self, form):
        """Save the new user, then add the user to the selected group"""
        group_obj = form.cleaned_data.get('select_group')
        email = form.cleaned_data.get('email')
        new_user = form.save(commit=False)
        if self.request.user.email != 'demo@ex.com':
            new_user.email = email
            new_user.save()
            new_user.groups.set([group_obj.id])
        messages.success(self.request, f"{new_user.username} is now a part of the team!")
        return redirect(reverse('issues:users-list'))
            

class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'issues/user_create_or_update.html'
    model = User
    form_class = UserForm

    def test_func(self):
        user_type = self.kwargs.get('type')
        if user_type == 'admin':
            return self.request.user.groups.filter(name='Admin').exists()
        elif user_type == 'std-user':
            return True if self.request.user == self.get_object() else False

    def get_object(self):
        name = self.kwargs.get('username')
        return get_object_or_404(self.model, username=name)
    
    def get_initial(self):
        user = self.get_object()
        group_id = user.groups.all()[0].id
        user_email = user.email
        return {'select_group': group_id, 'email': user_email}

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        form = self.form_class(initial=self.get_initial(), instance=user)
        context = {
            'user_obj': user,
            'form': form,
            'user_type': self.kwargs.get('type')
        }
        return render(request, self.template_name, context)
    
    def form_valid(self, form):
        group_obj = form.cleaned_data.get('select_group')
        email = form.cleaned_data.get('email')
        updated_user = form.save(commit=False)
        if self.request.user.email != 'demo@ex.com':
            updated_user.email = email
            updated_user.save()
            updated_user.groups.set([group_obj])

        if self.kwargs.get('type') == 'admin':
            messages.success(self.request, f"Profile for {updated_user.username} has been updated.")
            return redirect(reverse('issues:users-list'))
        else:
            messages.success(self.request, f"You profile has been updated.")
            return redirect(reverse('issues:my-profile', kwargs={'username': self.request.user.username}))
    
    def form_invalid(self, form):
        context = {
            'user_obj': self.get_object(),
            'form': form,
            'user_type': self.kwargs.get('type')
        }
        return render(self.request, self.template_name, context)


class ProjectsListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """Display all projects. Only Admins can view."""
    template_name = 'issues/projects_list.html'
    queryset = Project.objects.all()

    def test_func(self):
        return self.request.user.groups.filter(name='Admin').exists()


class MyProjectsView(LoginRequiredMixin, ListView):
    """Display all projects that have been assigned to the current user."""
    template_name = 'issues/my_projects_list.html'

    def get(self, request, *args, **kwargs):
        assigned_projects = request.user.assigned_projects.all()
        context = {
            'assigned_projects': assigned_projects,
        }
        return render(request, self.template_name, context)


class ProjectDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'issues/project_detail.html'
    model = Project

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_user_access = True if self.request.user in self.get_object().assigned_users.all() else False

        return admin_access or assigned_user_access
    
    def get(self, request, *args, **kwargs):
        project = self.get_object()
        assigned_users = project.assigned_users.all()
        if request.user.groups.filter(name='Admin').exists() or request.user.groups.filter(name='Project Manager').exists():
            issues = Issue.objects.filter(project=project.id)
        else:
            # For Developers and Submitters, only display the issues they are assigned to.
            issues = request.user.assigned_issues.filter(project=project.id)
        context = {
            'assigned_users': assigned_users,
            'project': project,
            'issues': issues
        }
        return render(request, self.template_name, context)


class ProjectCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'issues/project_create_or_update.html'
    model = Project
    form_class = ProjectForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        manager_access = self.request.user.groups.filter(name='Project Manager').exists()

        return admin_access or manager_access
    
    def form_valid(self, form):
        if self.request.user.email != 'demo@ex.com':
            new_proj = form.save()

            # Auto-assign managers to the projects they create.
            if self.request.user.groups.filter(name='Project Manager').exists():
                new_proj.assigned_users.add(self.request.user)
    
            return redirect(reverse('issues:project-detail', kwargs={'slug': new_proj.slug}))
        else:
            # Redirect demo user to project list and feign project creation.
            title = form.cleaned_data.get('title')
            messages.success(self.request, f"Project '{title}' has been created.")
            return redirect(reverse('issues:projects-list'))


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_object().assigned_users.all())

        return admin_access or assigned_manager_access
    
    def post(self, request, *args, **kwargs):
        project = self.get_object()
        if self.request.user.email != 'demo@ex.com':
            project.delete()
        messages.success(request, f"Project '{project.title}' has been successfully deleted.")
        return redirect(reverse('issues:projects-list'))


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'issues/project_create_or_update.html'
    model = Project
    form_class = ProjectForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_object().assigned_users.all())

        return admin_access or assigned_manager_access
    
    def form_valid(self, form):
        title = form.cleaned_data.get('title')
        if self.request.user.email != 'demo@ex.com':
            form.save()
        messages.success(self.request, f"Project '{title}' has been successfully updated.")
        return redirect(reverse('issues:project-detail', kwargs={'slug': self.object.slug}))


class ProjectAssignView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'issues/project_assign.html'

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())

        return admin_access or assigned_manager_access

    def get_project_object(self):
        slug_ = self.kwargs.get('slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get(self, request, *args, **kwargs):
        all_users = User.objects.filter(is_active=True)
        assigned_users = self.get_project_object().assigned_users.all()
        context = {
            'project': self.get_project_object(),
            'all_users': all_users,
            'assigned_users': assigned_users
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        user_ids = request.POST.getlist('selection')
        project = self.get_project_object()
        issues = project.issues.all()
        action = request.POST.get('action')
        username_list = []
        for user_id in user_ids:
            # Get list of names to display in success message.
            u = get_object_or_404(User, id=user_id)
            username_list.append(f"{u.username}")

            if action == 'assign' and not u in project.assigned_users.all() and self.request.user.email != 'demo@ex.com':
                project.assigned_users.add(u)
                # If the user is a project manager or admin, assign all project issues to them as well.
                if u.groups.filter(name='Admin').exists() or u.groups.filter(name='Project Manager').exists():
                    for issue in issues:
                        issue.assigned_users.add(u)

            elif action == 'unassign' and u in project.assigned_users.all() and self.request.user.email != 'demo@ex.com':
                project.assigned_users.remove(u)
                # Unassign the user from all project issues as well.
                for issue in issues:
                    issue.assigned_users.remove(u)

        users_str = get_users_str(username_list)

        if action == 'assign':
            messages.success(request, f"The following users have been assiged to project '{project.title}': {users_str}.")
        
        elif action == 'unassign':
            messages.success(request, f"The following users have been unassigned from project '{project.title}': {users_str}.")

        return redirect(reverse('issues:project-assign', kwargs={'slug': project.slug}))


class MyIssuesView(LoginRequiredMixin, View):
    """Display all issues that have been assigned to the current user."""
    template_name = 'issues/my_issues.html'

    def get(self, request, *args, **kwargs):
        assigned_issues = self.request.user.assigned_issues.all()
        context = {
            'issues': assigned_issues
        }
        return render(request, self.template_name, context)


class IssueCreateView(LoginRequiredMixin, CreateView):
    template_name = 'issues/issue_create_or_update.html'
    form_class = IssueForm

    def get(self, request, *args, **kwargs):
        context = {
            'form': self.form_class(user=request.user)
        }
        return render(request, self.template_name, context)
    
    def form_valid(self, form):
        new_issue = form.save(commit=False)
        if self.request.user.email != 'demo@ex.com':
            new_issue.submitter = self.request.user
            new_issue.save()

            # Assign all project managers (group id=2), the submitter, and the assignee to the new issue.
            project_managers = new_issue.project.assigned_users.filter(groups__in=[2])
            new_issue.assigned_users.add(self.request.user, new_issue.assignee, *project_managers)

            return redirect(reverse('issues:issue-detail', kwargs={'project_slug': new_issue.project.slug, 'issue_num': new_issue.num}))
        else:
            messages.success(self.request, f"Issue '{new_issue.title}' for project '{new_issue.project.title}' has been created.")
            return redirect(reverse('issues:my-issues'))


class ProjectIssueCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    template_name = 'issues/issue_create_or_update.html'
    model = Issue
    form_class = ProjectIssueForm
    context = {
        "form": form_class
    }

    def test_func(self):
        Admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_user_access = True if self.request.user in self.get_project_object().assigned_users.all() else False
        return Admin_access or assigned_user_access

    def get_project_object(self):
        slug_ = self.kwargs.get('slug')
        return get_object_or_404(Project, slug=slug_)

    def get(self, request, *args, **kwargs):
        self.context['project'] = self.get_project_object()
        return render(request, self.template_name, self.context)

    def form_valid(self, form):
        project = self.get_project_object()
        new_issue = form.save(commit=False)
        if self.request.user.email != 'demo@ex.com':
            new_issue.submitter = self.request.user
            new_issue.project = project
            new_issue.save()

            # Assign all project managers (group id=2), the submitter, and the assignee to the new issue.
            project_managers = project.assigned_users.filter(groups__in=[2])
            new_issue.assigned_users.add(self.request.user, new_issue.assignee, *project_managers)

            # If the assignee is not already assigned to the project, add them.
            if not new_issue.assignee in project.assigned_users.all():
                project.assigned_users.add(new_issue.assignee)

            return redirect(reverse('issues:issue-detail', kwargs={'project_slug': project.slug, 'issue_num': new_issue.num}))
        else:
            messages.success(self.request, f"Issue '{new_issue.title}' has been created.")
            return redirect(reverse('issues:project-detail', kwargs={'slug': project.slug}))
            

class IssueUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    template_name = 'issues/issue_create_or_update.html'
    form_class = ProjectIssueForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_user_access = True if self.request.user in self.get_object().assigned_users.all() else False
        return admin_access or assigned_user_access

    def get_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get(self, request, *args, **kwargs):
        issue = self.get_object()
        f = self.form_class(instance=issue)
        context = {
            'form': f,
            'issue': issue,
        }
        return render(request, self.template_name, context)
    
    def form_valid(self, form):
        issue = form.save(commit=False)
        if self.request.user.email != 'demo@ex.com':
            if issue.status == 'closed':
                issue.date_closed = datetime.datetime.now()
                # Unassign all users from the issue, so that their my-issues page isn't cluttered.
                issue.assigned_users.clear()
            issue.save()
        messages.success(self.request, f"Issue #{issue.num} has been successfully updated.")
        return redirect(reverse('issues:issue-detail', kwargs={'project_slug': self.get_project_object().slug, 'issue_num': issue.num}))


class IssueDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = 'issues/issue_detail.html'
    comment_form = CommentForm
    reply_form = ReplyForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_user_access = True if self.request.user in self.get_object().assigned_users.all() else False
        return admin_access or assigned_user_access

    def get_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get(self, request, *args, **kwargs):
        issue = self.get_object()
        issue_user_list = issue.assigned_users.all()
        comments = issue.comments.all().order_by('-date_created')
        replies = [Reply.objects.filter(comment=comment).order_by('date_created') for comment in comments]
        context = {
            'issue': self.get_object(),
            'issue_user_list': issue_user_list,
            'comment_form': self.comment_form,
            'reply_form': self.reply_form,
            'comments': comments,
            'replies': replies
        }
        return render(request, self.template_name, context)
    

class IssueDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_user_access = True if self.request.user in self.get_object().assigned_users.all() else False
        return admin_access or assigned_user_access
    
    def get_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)

    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)

    def post(self, request, *args, **kwargs):
        issue = self.get_object()
        issue_num = issue.num
        if self.request.user.email != 'demo@ex.com':
            issue.delete()
        messages.success(request, f"Issue #{issue_num} for project '{issue.project.title}' has been successfully deleted.")
        return redirect(reverse('issues:project-detail', kwargs={'slug': issue.project.slug}))


class IssueAssignView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = 'issues/issue_assign.html'

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())
        return admin_access or assigned_manager_access

    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def get(self, request, *args, **kwargs):
        project = self.get_project_object()
        issue = self.get_issue_object()
        issue_user_list = issue.assigned_users.all()
        project_user_list = project.assigned_users.all()
        context = {
            'issue': issue,
            'issue_user_list': issue_user_list,
            'project_user_list': project_user_list
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        user_ids = request.POST.getlist('selection')
        project = self.get_project_object()
        issue = self.get_issue_object()
        action = request.POST.get('action')
        username_list = []
        for user_id in user_ids:
            # Get list of names to display in success message.
            user = get_object_or_404(User, id=user_id)
            username = f"{user.username}"
            username_list.append(username)

            if action == 'assign' and not user in issue.assigned_users.all() and self.request.user.email != 'demo@ex.com':
                issue.assigned_users.add(user)

            elif action == 'unassign' and user in issue.assigned_users.all() and self.request.user.email != 'demo@ex.com':
                issue.assigned_users.remove(user)

        users_str = get_users_str(username_list)
        if action == 'assign':
            messages.success(request, f"The following users have been assiged to issue #{issue.num} of project '{project.title}': {users_str}.")
        elif action == 'unassign':
            messages.success(request, f"The following users have been removed from issue #{issue.num} of project '{project.title}': {users_str}.")

        return redirect(reverse('issues:issue-assign', kwargs={'project_slug': project.slug, 'issue_num': issue.num}))


class CommentCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = CommentForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())
        assigned_user_access = True if self.request.user in self.get_issue_object().assigned_users.all() else False
        return admin_access or assigned_manager_access or assigned_user_access
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            form = self.form_class(request.POST)
            if form.is_valid:
                if self.request.user.email != 'demo@ex.com':
                    issue = self.get_issue_object()
                    new_comment = form.save(commit=False)
                    new_comment.author = request.user
                    new_comment.issue = issue
                    new_comment.save()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({'error': form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Error: Request is not AJAX'}, status=400)


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = CommentForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())
        
        comment_id = self.request.POST.get('comment-id')
        comment_author = Comment.objects.get(id=comment_id).author
        author_access = True if self.request.user == comment_author else False

        return admin_access or assigned_manager_access or author_access
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            # Construct a form instance from the posted data to validate the updated comment.
            updated_text = request.POST.get('updated-text')
            comment_id = request.POST.get('comment-id')
            comment = get_object_or_404(Comment, id=comment_id)
            form = self.form_class({'text': updated_text}, instance=comment)
            if form.is_valid:
                if self.request.user.email != 'demo@ex.com':
                    form.save()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({'error': form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Error: Request is not AJAX'}, status=400)


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())

        comment_id = self.request.POST.get('comment-id')
        comment_author = Comment.objects.get(id=comment_id).author
        author_access = True if self.request.user == comment_author else False

        return admin_access or assigned_manager_access or author_access
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            if self.request.user.email != 'demo@ex.com':
                comment_id = request.POST.get('comment-id')
                comment = get_object_or_404(Comment, id=comment_id)
                comment.text = "[deleted]"
                comment.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'error': 'Error: Request is not AJAX'}, status=400)


class ReplyCreateView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = ReplyForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())
        assigned_user_access = True if self.request.user in self.get_issue_object().assigned_users.all() else False
        return admin_access or assigned_manager_access or assigned_user_access

    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            form = self.form_class(request.POST)
            if form.is_valid:
                if self.request.user.email != 'demo@ex.com':
                    comment_id = request.POST.get("comment-id")
                    new_reply = form.save(commit=False)
                    new_reply.author = request.user
                    new_reply.comment = get_object_or_404(Comment, id=comment_id)
                    new_reply.save()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({'error': form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Error: Request is not AJAX'}, status=400)


class ReplyDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):
    
    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())
        
        reply_id = self.request.POST.get('reply-id')
        reply_author = Reply.objects.get(id=reply_id).author
        author_access = True if self.request.user == reply_author else False

        return admin_access or assigned_manager_access or author_access
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            if self.request.user.email != 'demo@ex.com':
                reply_id = request.POST.get('reply-id')
                reply = get_object_or_404(Reply, id=reply_id)
                reply.text = "[deleted]"
                reply.save()
            return JsonResponse({}, status=200)
        else:
            return JsonResponse({'error': 'Error: Request is not AJAX'}, status=400)


class ReplyUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = ReplyForm

    def test_func(self):
        admin_access = self.request.user.groups.filter(name='Admin').exists()
        assigned_manager_access = self.request.user.groups.filter(name='Project Manager').exists() and (self.request.user in self.get_project_object().assigned_users.all())

        reply_id = self.request.POST.get('reply-id')
        reply_author = Reply.objects.get(id=reply_id).author
        author_access = True if self.request.user == reply_author else False

        return admin_access or assigned_manager_access or author_access
    
    def get_project_object(self):
        slug_ = self.kwargs.get('project_slug')
        return get_object_or_404(Project, slug=slug_)
    
    def get_issue_object(self):
        issue_num = self.kwargs.get('issue_num')
        return get_object_or_404(Issue, num=issue_num, project=self.get_project_object().id)
    
    def post(self, request, *args, **kwargs):
        if request.is_ajax:
            # Construct a form instance from the posted data to validate the updated reply.
            updated_text = request.POST.get('updated-text')
            reply_id = request.POST.get('reply-id')
            reply = get_object_or_404(Reply, id=reply_id)
            form = self.form_class({'text': updated_text}, instance=reply)
            if form.is_valid:
                if self.request.user.email != 'demo@ex.com':
                    form.save()
                return JsonResponse({}, status=200)
            else:
                return JsonResponse({'error': form.errors}, status=400)
        else:
            return JsonResponse({'error': 'Error: Request is not AJAX'}, status=400)


class MyProfileView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'issues/my_profile.html'

    def test_func(self):
        return True if self.request.user == self.get_user_object() else False
    
    def get_user_object(self):
        name = self.kwargs.get('username')
        return get_object_or_404(User, username=name)

    def get(self, request, *args, **kwargs):
        context = {
            'user': self.get_user_object,
            'user_type': 'std-user'
        }
        return render(request, self.template_name, context)


class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, View):

    def test_func(self):
        return True if self.request.user == self.get_user_object() else False
    
    def get_user_object(self):
        name = self.kwargs.get('username')
        return get_object_or_404(User, username=name)
    
    def post(self, request, *args, **kwargs):
        user = self.get_user_object()
        if self.request.user.email != 'demo@ex.com':
            user.is_active = False
            user.save()
        messages.success(self.request, f"Your account has been successfully deleted.")
        return redirect(reverse('login'))
