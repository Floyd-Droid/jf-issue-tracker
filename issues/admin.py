from django.contrib import admin
from .models import (
    Project,
    Issue,
    Comment,
    Reply
)

model_list = [Project, Issue, Comment, Reply]
admin.site.register(model_list)
