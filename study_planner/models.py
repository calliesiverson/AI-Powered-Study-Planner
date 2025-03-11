from django.db import models
from django.contrib.auth.models import User

class StudyTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    generated_by_ai = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class UserPoints(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"

class Achievement(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    points_needed = models.IntegerField()

    def __str__(self):
        return self.name


