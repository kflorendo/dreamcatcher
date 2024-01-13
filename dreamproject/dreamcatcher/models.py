from django.db import models
from django.contrib.auth.models import User


class DreamSequence(models.Model):
    user = models.ForeignKey(User, default=None, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    hydration = models.IntegerField(default=0)
    interpretation = models.TextField()
    sentiment = models.CharField(max_length=50)
    image = models.FileField(blank=True)
    content_type = models.CharField(max_length=50, default="image/jpeg")


class DreamChunk(models.Model):
    sequence = models.ForeignKey(DreamSequence, on_delete=models.PROTECT)
    text = models.TextField()
    image = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    context = models.CharField(max_length=500)
    picture = models.FileField(blank=True)
    content_type = models.CharField(max_length=50)
    following = models.ManyToManyField(User, related_name="following")
