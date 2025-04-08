from django.contrib import admin
from .models import StudyTask, UserPoints, UserStreak, Achievement

admin.site.register(StudyTask)
admin.site.register(UserPoints)
admin.site.register(UserStreak)
admin.site.register(Achievement)
