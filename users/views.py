from django.contrib.auth import authenticate, login
from django.views import View
from django.shortcuts import render, redirect
from .forms import UserCreationForm  # Make sure this file exists


# REGISTER VIEW
class Register(View):
    template_name = 'registration/register.html'

    def get(self, request):
        context = {'form': UserCreationForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('users:home')  # Use namespaced URL
        context = {'form': form}
        return render(request, self.template_name, context)


# HOME VIEW - THIS WAS MISSING!
def home(request):
    return render(request, 'home.html')