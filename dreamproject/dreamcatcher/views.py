from django.shortcuts import render

# Create your views here.
def landing(request):
    return render(request, 'dreamcatcher/landing.html', {})

def new_dream(request):
    return render(request, 'dreamcatcher/new-dream.html', {})