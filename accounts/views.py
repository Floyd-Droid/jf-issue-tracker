from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse

from django.views.generic import CreateView

# Create your views here.


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        new_user = form.save()
        # Every new user will be a manager (group id=2) by default.
        new_user.groups.set([2])
        login(self.request, user=new_user)
        messages.success(self.request, f"Welcome to the site! From here, you can create projects and keep track of related issues. Only you can see the projects, issues, and comments you create. To see a full demonstration of site functionality (without the ability to make changes to the database), log in as a demo user.")
        return redirect(reverse('issues:my-projects'))
