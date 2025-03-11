from django.db import models
from django.contrib.auth.models import User

from django.db import models

class StudyTask(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


# class Reward(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     points = models.IntegerField(default=0)
#     badge = models.CharField(max_length=100, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.points} points"
