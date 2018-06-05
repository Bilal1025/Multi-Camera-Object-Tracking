from django.contrib.auth.models import User
from django.db import models


class Cameras(models.Model):
    name = models.CharField(max_length=30, unique=True)
    ipaddr = models.TextField(primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    thumbnail = models.CharField(max_length=1000)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)

class Neighbours(models.Model):
    id = models.AutoField(primary_key=True)
    camera1 = models.ForeignKey(Cameras,on_delete=models.CASCADE,related_name="Camera1")
    camera2 = models.ForeignKey(Cameras, on_delete=models.CASCADE, related_name="Camera2")

class Videos(models.Model):
    name = models.CharField(max_length=50,primary_key=True)
    path = models.CharField(max_length=1000)
    thumbnail = models.CharField(max_length=1000)
    userid = models.ForeignKey(User, on_delete=models.CASCADE)

class VideoNeighbours(models.Model):
    id = models.AutoField(primary_key=True)
    video1 = models.ForeignKey(Videos,on_delete=models.CASCADE,related_name="Video1")
    video2 = models.ForeignKey(Videos, on_delete=models.CASCADE, related_name="Video2")