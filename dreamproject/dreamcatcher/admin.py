from django.contrib import admin

# Register your models here.
from .models import DreamSequence, DreamChunk, Profile

admin.site.register(DreamSequence)
admin.site.register(DreamChunk)
admin.site.register(Profile)
