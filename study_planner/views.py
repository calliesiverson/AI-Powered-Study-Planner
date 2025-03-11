from django.shortcuts import render, redirect
from .models import StudyTask
from .utils import generate_study_plan
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after signing up
            return redirect('home')  # Redirect to home page after successful signup
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})


def home(request):
    tasks = StudyTask.objects.all()  # Fetch tasks from the database
    study_plan = None  # Default to None

    if request.method == "POST":
        task_title = request.POST.get("task_title")  # Get input from user
        if task_title:  # Ensure task title isn't empty
            study_plan = generate_study_plan(task_title, list(tasks))  # Generate study plan
            
            # if request.user.is_authenticated:
            #     user_points = UserPoints.objects.get(user=request.user)
            #     user_points.points += 10  # Award points for task completion
            #     user_points.save()

    # If study_plan is a list, access the first item (the dictionary) to get its data
    if isinstance(study_plan, list) and study_plan:
        study_plan_data = study_plan[0]  # Get the first dictionary in the list
        goal = study_plan_data.get("goal", "Not available")
        time_commitment = study_plan_data.get("time_commitment", "Not available")
        recommended_resources = study_plan_data.get("recommended_resources", "Not available")
        weekly_breakdown = study_plan_data.get("weekly_breakdown", "Not available")
        daily_breakdown = study_plan_data.get("daily_breakdown_example", "Not available")
        tips = study_plan_data.get("tips", "Not available")
    else:
        # If study_plan is not a list or is empty, set everything to "Not available"
        goal = time_commitment = recommended_resources = weekly_breakdown = daily_breakdown = tips = "Not available"

    return render(request, "home.html", {
        "tasks": tasks,
        "study_plan": study_plan,
        "goal": goal,
        "time_commitment": time_commitment,
        "recommended_resources": recommended_resources,
        "weekly_breakdown": weekly_breakdown,
        "daily_breakdown": daily_breakdown,
        "tips": tips
        #"user_points": user_points.points if request.user.is_authenticated else 0
    })

def award_achievements(user):
    achievements = Achievement.objects.all()
    unlocked_achievements = []

    user_points = UserPoints.objects.get(user=user)
    for achievement in achievements:
        if user_points.points >= achievement.points_needed:
            unlocked_achievements.append(achievement)

    return unlocked_achievements

