from django.shortcuts import render

# Create your views here.
def landing(request):
    return render(request, 'dreamcatcher/landing.html', {})

def entry(request):
    return render(request, 'dreamcatcher/entry.html', {})