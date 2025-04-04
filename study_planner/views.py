from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages 
from .models import StudyTask, UserStreak, Achievement, UserPoints
from .utils import generate_study_plan
import logging
import Levenshtein


logger = logging.getLogger(__name__)                ## Logger for debugging

def login(request):                                 ## Function to login to the system
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # Redirect to homepage
    else:
        form = AuthenticationForm()
    return render(request, "accounts/login.html", {"form": form})

def signup(request):                                ## Function to signup with an account
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log user in after signup
            return redirect("home")  # Redirect to homepage
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})

def similar(existing_task, new_task, threshold=0.8):
    similarity_ratio = Levenshtein.ratio(existing_task.lower(), new_task.lower())

    return similarity_ratio >= threshold

@login_required                 # Required to be logged in to access the home page
def home(request):              # Function to render study plan variable to be used in the home page
    tasks = StudyTask.objects.filter(user=request.user)  # Fetch user's tasks
    study_plan = None

    # Initialize study plan variables
    goal = time_commitment = recommended_resources = weekly_breakdown = daily_breakdown = tips = "Not available"

    if request.method == "POST":
        user = request.user
        task_title = request.POST.get("task_title")

        if len(task_title) > 100:
            messages.error(request, "THE TASK MUST BE 100 CHARACTERS OR LESS")
            return redirect('home')

        existing_task = StudyTask.objects.filter(task__iexact=task_title).first()

        if existing_task:
            messages.error(request, "STUDY PLAN OF SAME NAME ALREADY EXISTS")
            return redirect('home')

        # existing_tasks = StudyTask.objects.filter(user=request.user)
        for task in tasks:
            if similar(task.task, task_title):
                messages.error(request, "SIMILAR STUDY PLAN ALREADY EXISTS")
                return redirect('home')

        if task_title:
            study_plan = generate_study_plan(task_title, list(tasks))  # Call AI response function

            if isinstance(study_plan, dict):  # Ensure valid response
                goal = study_plan.get("goal", "Not available")
                time_commitment = study_plan.get("time_commitment", "Not available")
                recommended_resources = study_plan.get("recommended_resources", [])
                weekly_breakdown = study_plan.get("weekly_breakdown", [])
                daily_breakdown = study_plan.get("daily_breakdown", [])  # FIXED!
                tips = study_plan.get("tips", [])

                study_task = StudyTask.objects.create(
                    user=request.user,
                    task=task_title,
                    goal=goal,
                    time_commitment=time_commitment,
                    recommended_resources=recommended_resources,
                    weekly_breakdown=weekly_breakdown,
                    daily_breakdown=daily_breakdown,
                    study_tips=tips
                )

                # # Add points after study session completion... still in the process of implementation
                # user_points = UserPoints.objects.get(user=request.user)
                # points_earned = 10  # Example points awarded
                # user_points.add_points(points_earned)

                # # Update streak... still in the process of implementation
                # study_streak, created = StudyStreak.objects.get_or_create(user=request.user)
                # study_streak.update_streak(date.today())

                messages.success(request, "Study plan saved successfully!")
                return redirect('home')

    return render(request, "home.html", {           ## Render the home page with the following study plan variables
        "tasks": tasks,           
        "study_plan": study_plan,
        "goal": goal,
        "time_commitment": time_commitment,
        "recommended_resources": recommended_resources,
        "weekly_breakdown": weekly_breakdown,
        "daily_breakdown": daily_breakdown,
        "tips": tips
    })

@login_required
def past_study_plans(request):                  ## Function to render past study plans saved into the database
    study_plans = StudyTask.objects.filter(user=request.user)
    return render(request, "past_study_plans.html", {"study_plans": study_plans})

@login_required
def study_task_detail(request, task_id):        ## Function to render the details of a specific study task chosen by the user
    task = get_object_or_404(StudyTask, id=task_id)
    return render(request, "study_task_detail.html", {"task": task})

@login_required
def delete_study_plan(request, plan_id):
    study_plan = get_object_or_404(StudyTask, id=plan_id)

    if request.method == 'POST':
        study_plan.delete()  # This deletes the study plan from the database
        return redirect('past_study_plans')  # Redirect to the past study plans page (or wherever you want)

    return render(request, 'confirm_delete.html', {'study_plan': study_plan})
# @login_required
# def update_streak(request):                     ## Function to update the user's study streak as they login and study... still in the process of implementation
#     user_streak, _ = UserStreak.objects.get_or_create(user=request.user)
#     today = now().date()

#     if user_streak.last_study_date == today:
#         return JsonResponse({'message': 'Streak already updated today.'})

#     user_streak.update_streak(today)            ## Update the user's streak

#     achievements = Achievement.objects.filter(streak_needed__lte=user_streak.current_streak)        ## Check for streak-based achievements and award them to the user
#     for achievement in achievements:
#         achievement.award_to_user(request.user)

#     return JsonResponse({'message': f'Streak updated! Current streak: {user_streak.current_streak}'})

# @login_required
# def award_points(request):                      ## Function to award points to the user as they complete tasks
#     user_points, _ = UserPoints.objects.get_or_create(user=request.user)
#     points_to_award = 10  # May change this value as needed

#     user_points.add_points(points_to_award)

#     achievements = Achievement.objects.filter(points_needed__lte=user_points.points)        ## Check for point-based achievements and award them to the user
#     for achievement in achievements:
#         achievement.award_to_user(request.user)

#     return JsonResponse({'message': f'Points awarded! Total points: {user_points.points}'})


# @login_required
# def complete_quiz(request):                 ## Function to award points to the user as they complete a quiz
#     user_points, _ = UserPoints.objects.get_or_create(user=request.user)
#     quiz_bonus_points = 20  # May change as needed

#     user_points.add_points(quiz_bonus_points)       ## Award the user with the bonus points depending on correct answers

#     return JsonResponse({'message': f'Quiz completed! {quiz_bonus_points} points awarded.'})

# @login_required
# def user_achievements(request):             ## Function to display the user's achievements
#     achievements = Achievement.objects.filter(users_earned=request.user)
#     data = [{'name': ach.name, 'description': ach.description} for ach in achievements]
    
#     return JsonResponse({'achievements': data})