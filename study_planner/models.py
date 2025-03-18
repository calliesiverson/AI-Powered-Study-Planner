from django.db import models
from django.contrib.auth.models import User
from datetime import date

class StudyTask(models.Model):                              ## StudyTask model for the database
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    task = models.CharField(max_length=255, default="No study task available.")
    goal = models.TextField(default="No goal provided.") 
    time_commitment = models.CharField(max_length=100, default="No time commitment specified.")
    recommended_resources = models.JSONField(default=dict)
    weekly_breakdown = models.JSONField(default=list)
    daily_breakdown = models.JSONField(default=list)
    study_tips = models.JSONField(default=list)
    progress = models.IntegerField(default=0)
    
    def __str__(self):
        return self.task


class UserPoints(models.Model):                             ## UserPoints model for the database... still in the process of implementation
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def add_points(self, amount):
        self.points += amount
        self.save()
        self.check_achievements()

    def check_achievements(self):
        unlocked_achievements = Achievement.objects.filter(points_needed__lte=self.points)
        for achievement in unlocked_achievements:
            achievement.award_to_user(self.user)

    def __str__(self):
        return f"{self.user.username} - {self.points} points"


class UserStreak(models.Model):                             ## UserStreak model for the database... still in the process of implementation             
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    current_streak = models.IntegerField(default=0)
    longest_streak = models.IntegerField(default=0)
    last_study_date = models.DateField(null=True, blank=True)

    def update_streak(self, study_date):
        if self.last_study_date is None or (today - self.last_study_date).days > 1:
            self.current_streak = 1  # Reset streak if they skipped a day
        else:
            self.current_streak += 1  # Increase streak

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak  # Update longest streak

        self.last_study_date = study_date
        self.save()
        self.check_streak_achievements()

    def check_streak_achievements(self):
        unlocked_achievements = Achievement.objects.filter(streak_needed__lte=self.current_streak)
        for achievement in unlocked_achievements:
            achievement.award_to_user(self.user)

    def __str__(self):
        return f"{self.user.username} - Streak: {self.current_streak}, Longest: {self.longest_streak}"


class Achievement(models.Model):                            ## Achievement model for the database... still in the process of implementation
    name = models.CharField(max_length=255)
    description = models.TextField()
    points_needed = models.IntegerField(null=True, blank=True)
    streak_needed = models.IntegerField(null=True, blank=True)
    users_earned = models.ManyToManyField(User, blank=True)

    def award_to_user(self, user):
        if user not in self.users_earned.all():
            self.users_earned.add(user)
            self.save()

    def __str__(self):
        return self.name
