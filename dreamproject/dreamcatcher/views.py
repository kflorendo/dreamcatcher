from dreamcatcher.functions.get_dream_analysis import *
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone, dateformat

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from dreamcatcher.forms import LoginForm, RegisterForm

from django.http import HttpResponse


from dreamcatcher.models import *
from dreamcatcher.functions.get_dream_question import *
from dreamcatcher.functions.generate_dream_image import *

from django.core.files.base import ContentFile


from dreamcatcher.functions.dream_embeddings import embed_and_store_dream, get_similar_dream_ids

HYDRATION = 20


# Create your views here.


def landing(request):
    return render(request, "dreamcatcher/landing.html", {})


@login_required
def entry(request):
    context = {}
    context['question'] = 'About last night...'
    context["sequence_id"] = ""
    return render(request, "dreamcatcher/entry.html", context)


@login_required
def process_entry(request):
    context = {}
    context['question'] = 'About last night...'

    # Adds the new item to the database if the request parameter is present
    if "dream-text-input" not in request.POST or not request.POST["dream-text-input"]:
        # If error, redirect to global stream with error message
        # TODO: display error
        print("dream text not present")
        return render(request, "dreamcatcher/entry.html", {})

    dream_text = request.POST["dream-text-input"]
    word_len = len(dream_text.split())

    # Check if sequence was already created
    if "sequence-id" not in request.POST:
        # If error, redirect to global stream with error message
        # TODO: display error
        print("sequence field not present")
        return render(request, "dreamcatcher/entry.html", context)

    sequence_id = request.POST["sequence-id"]
    if sequence_id == "":
        # Create initial sequence with one chunk
        formatted_date = dateformat.format(timezone.now(), "Y-m-d H:i:s")
        dream_title = f"My Dream {formatted_date}"
        sequence = DreamSequence(
            user=request.user,
            title=dream_title,
            hydration=word_len,
            interpretation="",
            sentiment="",
            date_time=timezone.now(),
        )
        sequence.save()
    else:
        sequence = get_object_or_404(DreamSequence, pk=int(sequence_id))
        sequence.hydration += word_len
        sequence.save()

    context = {}

    complete_dream_text = ""
    chunks = DreamChunk.objects.filter(sequence=sequence)
    for chunk in chunks:
        complete_dream_text += chunk.text + " "

    dream_question = get_dream_question(complete_dream_text)
    context["question"] = dream_question

    new_chunk = DreamChunk(
        sequence=sequence, text=dream_text, image="", content_type=""
    )
    new_chunk.save()

    # Check hydration
    if sequence.hydration < HYDRATION:
        context["sequence_id"] = str(sequence.id)

        return render(request, "dreamcatcher/entry.html", context)
    else:
        # Fetch all DreamChunk texts for this sequence
        complete_dream_text = ""
        chunks = DreamChunk.objects.filter(sequence=sequence)
        for chunk in chunks:
            complete_dream_text += chunk.text + " "

        # Perform dream analysis
        # Replace 'get_dream_analysis' with your actual analysis function
        interpretation = get_dream_analysis(complete_dream_text)

        sequence.interpretation = interpretation
        sequence.save()

        # generate image from the complete_dream_text
        image_data = generate_dream_image(complete_dream_text)

        # Convert PIL JpegImageFile to a BytesIO object
        image_io = BytesIO()
        image_data.save(image_io, format="JPEG")
        image_io.seek(0)

        # Create a Django ContentFile from the BytesIO object
        image_file = ContentFile(image_io.read(), name="dream_image.jpg")

        # Save the image to the sequence model
        sequence.image.save("dream_image.jpg", image_file, save=True)
        # sequence.content_type = ssequence.image.content_type
        sequence.save()

        embed_and_store_dream(str(sequence.id), complete_dream_text)
        print("embedded dream", sequence.id)

        return redirect("home")


@login_required
def home(request):
    return render(request, "dreamcatcher/home.html", {})


@login_required
def profile(request):
    return render(request, "dreamcatcher/profile.html", {})


@login_required
def dream_list(request):
    context = {}
    dream_list = DreamSequence.objects.all().filter(
        user=request.user).order_by('-date_time')
    dreams = []
    for dream in dream_list:
        # print(dream.dreamchunk_set.all()[0].text)
        preview_text = dream.dreamchunk_set.all()[0].text
        dreams.append({'title': dream.title, 'date': dream.date_time.strftime(
            '%Y.%m.%d %H:%M'), 'preview': preview_text, "id": dream.id})
        # previews.append(dream.dreamchunk_set.all()[0].text)
    context["dreams"] = dreams
    return render(request, "dreamcatcher/dream-list.html", context)


@login_required
def view_dream_sequence(request, id):
    ds = get_object_or_404(DreamSequence, pk=id)
    dreamchunks = DreamChunk.objects.filter(sequence=id)
    return render(
        request,
        "dreamcatcher/dream_display_seq.html",
        {"sequence": ds, "dreamchunks": dreamchunks},
    )


@login_required
def view_dream_analysis(request, id):
    ds = get_object_or_404(DreamSequence, pk=id)
    return render(request, "dreamcatcher/dream_display_analysis.html", {"sequence": ds})


@login_required
def get_image_action(request, id):
    sequence = get_object_or_404(DreamSequence, id=id)

    # Checks if picture was deleted from the DB
    if not sequence.image:
        raise Http404

    return HttpResponse(sequence.image, content_type=sequence.content_type)


@login_required
def view_related_dreams(request, id):
    ds = get_object_or_404(DreamSequence, pk=id)
    preview_text = ds.dreamchunk_set.all()[0].text
    main_dream = {'title': ds.title, 'date': ds.date_time.strftime(
        '%Y.%m.%d %H:%M'), 'preview': preview_text}

    ids = get_similar_dream_ids(str(id), 5)
    print("related dreams", ids)

    dreams = []
    for id in ids:
        dream = DreamSequence.objects.get(pk=id)
        preview_text = dream.dreamchunk_set.all()[0].text
        dreams.append({'title': dream.title, 'date': dream.date_time.strftime(
            '%Y.%m.%d %H:%M'), 'preview': preview_text, "id": id})

    return render(request, 'dreamcatcher/dream_display_similar.html', {"dreams": dreams, "dream": main_dream, "sequence": ds})


def login_action(request):
    context = {}

    # Just display the login form if this is a GET request.
    if request.method == "GET":
        context["form"] = LoginForm()
        return render(request, "dreamcatcher/login.html", context)
    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = LoginForm(request.POST)
    context["form"] = form

    # Validates the form
    if not form.is_valid():
        return render(request, "dreamcatcher/login.html", context)

    user = authenticate(
        username=form.cleaned_data["username"], password=form.cleaned_data["password"]
    )
    login(request, user)

    return redirect(reverse("home"))


def register_action(request):
    context = {}

    # Just display the register form if this is a GET request.
    if request.method == "GET":
        context["form"] = RegisterForm()
        return render(request, "dreamcatcher/register.html", context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegisterForm(request.POST)
    context["form"] = form

    # Validates the form
    if not form.is_valid():
        return render(request, "dreamcatcher/register.html", context)

    # Since the form data is valid, register and login the user
    new_user = User.objects.create_user(
        username=form.cleaned_data["username"],
        password=form.cleaned_data["password"],
        email=form.cleaned_data["email"],
        first_name=form.cleaned_data["first_name"],
        last_name=form.cleaned_data["last_name"],
    )
    new_user.save()

    # Authenticate the user
    new_user = authenticate(
        username=form.cleaned_data["username"], password=form.cleaned_data["password"]
    )
    login(request, new_user)

    # Create user profile
    new_profile = Profile(user=new_user, picture="", content_type="")
    new_profile.save()

    return redirect(reverse("home"))


def logout_action(request):
    logout(request)
    return redirect(reverse("login"))
