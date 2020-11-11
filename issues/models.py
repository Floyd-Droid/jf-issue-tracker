from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone

def get_issue_num(project):
    """Get the most recent issue number of a project and return an incremented value."""
    last_project_issue = Issue.objects.filter(project=project.id).order_by('id').last()
    if not last_project_issue:
        return 1
    else:
        return last_project_issue.num + 1


class Project(models.Model):
    
    title = models.CharField(
        max_length=100,
        unique=True,
        error_messages={'unique':'A project with this title already exists.'}
    )

    description = models.TextField()
    slug = models.SlugField(max_length=100, unique=True)
    assigned_users = models.ManyToManyField(User, related_name='assigned_projects')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Project, self).save(*args, **kwargs)


class Issue(models.Model):

    PRIORITY_CHOICES = (
        (1, '1 - Very High'),
        (2, '2 - High'),
        (3, '3 - Medium'),
        (4, '4 - Low'),
        (5, '5 - Very Low')
    )

    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = (
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    )

    TYPE_BUG = 'bug'
    TYPE_FEATURE = 'feature'
    TYPE_OTHER = "other"

    TYPE_CHOICES = (
        (TYPE_BUG, 'Bug'),
        (TYPE_FEATURE, 'Feature'),
        (TYPE_OTHER, "Other")
    )

    title = models.CharField(max_length=150)
    description = models.TextField()

    num = models.IntegerField(editable=False)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_closed = models.DateTimeField(blank=True, null=True)

    submitter = models.ForeignKey(
        User,
        related_name='issue_submitter', 
        on_delete=models.CASCADE
    )

    assignee = models.ForeignKey(
        User, 
        related_name='issue_assignee',
        blank=True,
        null=True, 
        on_delete=models.CASCADE
    )

    assigned_users = models.ManyToManyField(User, related_name='assigned_issues')

    project = models.ForeignKey(
        Project,
        related_name='issues',
        on_delete=models.CASCADE,
    )

    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        default=3,
        blank=3,
    )

    status = models.CharField(
        max_length=9, 
        choices=STATUS_CHOICES, 
        default=STATUS_OPEN
    )

    issue_type = models.CharField(
        max_length=7, 
        choices=TYPE_CHOICES, 
        default=TYPE_BUG
    )

    tag = models.CharField(max_length=40, blank=True, null=True)
    attachment = models.ImageField(upload_to='img', blank=True, null=True)

    def __str__(self):
        return self.title
     
    def save(self, *args, **kwargs):
        # Pass the project object to get_issue_num to generate the newest issue number for the project.
        # When editing an issue, the num field already has a value, so don't increment.
        if not self.num:
            self.num = get_issue_num(self.project)
        super(Issue, self).save(*args, **kwargs)


class Comment(models.Model):
    """A single top-level comment."""

    text = models.TextField()
    author = models.ForeignKey(User,
        related_name='comments',
        on_delete=models.CASCADE
    )

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    issue = models.ForeignKey(
        Issue, 
        related_name='comments',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.text


class Reply(models.Model):
    """A reply to a comment."""

    text = models.TextField()
    author = models.ForeignKey(User, related_name='replies', on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='replies', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.text
