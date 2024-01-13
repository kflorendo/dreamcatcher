from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone, dateformat

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from dreamcatcher.forms import LoginForm, RegisterForm

from dreamcatcher.models import *

HYDRATION = 10

# Create your views here.


def landing(request):
    return render(request, 'dreamcatcher/landing.html', {})


@login_required
def entry(request):
    context = {}
    context['sequence_id'] = ''
    return render(request, 'dreamcatcher/entry.html', context)


@login_required
def process_entry(request):
    # Adds the new item to the database if the request parameter is present
    if 'dream-text-input' not in request.POST or not request.POST['dream-text-input']:
        # If error, redirect to global stream with error message
        # TODO: display error
        print('dream text not present')
        return render(request, 'dreamcatcher/entry.html', {})

    dream_text = request.POST['dream-text-input']
    word_len = len(dream_text.split())

    # Check if sequence was already created
    if 'sequence-id' not in request.POST:
        # If error, redirect to global stream with error message
        # TODO: display error
        print('sequence field not present')
        return render(request, 'dreamcatcher/entry.html', {})

    sequence_id = request.POST['sequence-id']
    if sequence_id == '':
        # Create initial sequence with one chunk
        formatted_date = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        dream_title = f'My Dream {formatted_date}'
        sequence = DreamSequence(user=request.user, title=dream_title, hydration=word_len,
                                 interpretation='', sentiment='', date_time=timezone.now())
        sequence.save()
    else:
        sequence = get_object_or_404(DreamSequence, pk=int(sequence_id))
        sequence.hydration += word_len
        sequence.save()

    new_chunk = DreamChunk(
        sequence=sequence, text=dream_text, image='', content_type='')
    new_chunk.save()

    # Check hydration
    if sequence.hydration < HYDRATION:
        context = {}
        context['sequence_id'] = str(sequence.id)
        return render(request, 'dreamcatcher/entry.html', context)
    else:
        return redirect('home')


@login_required
def home(request):
    return render(request, 'dreamcatcher/home.html', {})


@login_required
def view_dream_sequence(request, id):
    ds = get_object_or_404(DreamSequence, pk=id)
    dreamchunks = DreamChunk.objects.filter(sequence=id)
    return render(request, 'dreamcatcher/dream_display_seq.html', {"dreamchunks": dreamchunks})


@login_required
def view_dream_analysis(request, id):
    ds = get_object_or_404(DreamSequence, pk=id)
    return render(request, 'dreamcatcher/dream_display_analysis.html', {"analysis": ds.interpretation})


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
