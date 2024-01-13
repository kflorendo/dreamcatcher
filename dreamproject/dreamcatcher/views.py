from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from dreamcatcher.forms import LoginForm, RegisterForm

from dreamcatcher.models import *

# Create your views here.
def landing(request):
    return render(request, 'dreamcatcher/landing.html', {})

@login_required
def entry(request):
    return render(request, 'dreamcatcher/entry.html', {})

@login_required
def home(request):
    return render(request, 'dreamcatcher/home.html', {})

def login_action(request):
    context = {}

    # Just display the login form if this is a GET request.
    if request.method == 'GET':
        context['form'] = LoginForm()
        return render(request, 'dreamcatcher/login.html', context)
    
    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context['form'] = form

    # Validates the form
    if not form.is_valid():
        return render(request, 'dreamcatcher/login.html', context)

    user = authenticate(username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'])
    login(request, user)

    return redirect(reverse('home'))

def register_action(request):
    context = {}

    # Just display the register form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'dreamcatcher/register.html', context)
    
    # Creates a bound form from the request POST parameters and makes the 
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context['form'] = form

    # Validates the form
    if not form.is_valid():
        return render(request, 'dreamcatcher/register.html', context)
    
    # Since the form data is valid, register and login the user
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    new_user.save()

    # Authenticate the user
    new_user = authenticate(username=form.cleaned_data['username'],
                            password=form.cleaned_data['password'])
    login(request, new_user)

    # Create user profile
    new_profile = Profile(user=new_user, picture="", content_type="")
    new_profile.save()

    return redirect(reverse('home'))

def logout_action(request):
    logout(request)
    return redirect(reverse('login'))