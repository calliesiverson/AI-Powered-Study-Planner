from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages 
import logging
import json
from .models import StudyTask, UserStreak, Achievement, UserPoints
from .utils import generate_study_plan
from datetime import date, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

def similar(existing_task, new_task):
    # Extract the task field as a string
    existing_task_title = existing_task.task.lower()
    new_task_title = new_task.lower()
    
    # Now apply TfidfVectorizer to the extracted titles
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform([existing_task_title, new_task_title])
    
    # Calculate cosine similarity between the two tasks
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

    feature_names = vectorizer.get_feature_names_out()

    print()
    print("Tokens:", feature_names)
    print("Cosine similarity:", similarity[0][0])  # Print the similarity score for debugging
    print()

    return similarity[0][0]

@login_required                 # Required to be logged in to access the home page
def home(request):              # Function to render study plan variable to be used in the home page
    tasks = StudyTask.objects.filter(user=request.user)  # Fetch user's tasks
    study_plan = None
    user_points, created = UserPoints.objects.get_or_create(user=request.user, defaults={'points': 0})
    user_streak, created = UserStreak.objects.get_or_create(user=request.user, defaults={'current_streak': 0})


    # Initialize study plan variables
    goal = time_commitment = recommended_resources = weekly_breakdown = daily_breakdown = tips = "Not available"

    if request.method == "POST":
        # user = request.user
        task_title = request.POST.get("task_title")

        if len(task_title) > 100:                                                   # Requires task to be 100 characters or less
            messages.error(request, "THE TASK MUST BE 100 CHARACTERS OR LESS")
            return redirect('home')

        existing_task = StudyTask.objects.filter(user=request.user, task__iexact=task_title).first()   # Checks if the inputted task is the same as other past tasks

        if existing_task:
            messages.error(request, "STUDY PLAN OF SAME NAME ALREADY EXISTS")
            return redirect('home')

        existing_tasks = StudyTask.objects.filter(user=request.user)

        for task in existing_tasks:
            if similar(task, task_title) >= 0.70:                                      # Uses cosine similarity to check if the inputted task is similar to other past tasks
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

                # Add points after study session completion... still in the process of implementation
                user_points = UserPoints.objects.get(user=request.user)
                points_earned = 10  # Example points awarded
                user_points.add_points(points_earned)

                # Update streak... still in the process of implementation
                user_streak, created = UserStreak.objects.get_or_create(user=request.user)
                # user_streak.update_streak(date.today())

                messages.success(request, "Study plan saved successfully!")

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
def delete_study_plan(request, task_id):
    study_plan = get_object_or_404(StudyTask, id=task_id)

    if request.method == 'POST':
        study_plan.delete()  # This deletes the study plan from the database
        return redirect('past_study_plans')  # Redirect to the past study plans page (or wherever you want)

    return render(request, 'confirm_delete.html', {'study_plan': study_plan})

###########################
## Gamification elements ## 
###########################

@login_required
def update_streak(request):                     ## Function to update the user's study streak as they login and study... still in the process of implementation
    today = now().date()
    
    user_streak, _ = UserStreak.objects.get_or_create(user=request.user)

    if user_streak.last_study_date == today:
        return JsonResponse({'message': 'Streak already updated today.'})

    user_streak.update_streak(today)            ## Update the user's streak

    achievements = Achievement.objects.filter(streak_needed__lte=user_streak.current_streak)        ## Check for streak-based achievements and award them to the user
    for achievement in achievements:
        achievement.award_to_user(request.user)

    return JsonResponse({'message': f'Streak updated! Current streak: {user_streak.current_streak}'})

@login_required
def award_points(request):                      ## Function to award points to the user as they complete tasks
    user_points, _ = UserPoints.objects.get_or_create(user=request.user)
    points_to_award = 10  # May change this value as needed

    user_points.add_points(points_to_award)

    achievements = Achievement.objects.filter(points_needed__lte=user_points.points)        ## Check for point-based achievements and award them to the user
    for achievement in achievements:
        achievement.award_to_user(request.user)

    return JsonResponse({'message': f'Points awarded! Total points: {user_points.points}'})


@login_required
def complete_quiz(request):                 ## Function to award points to the user as they complete a quiz
    user_points, _ = UserPoints.objects.get_or_create(user=request.user)
    quiz_bonus_points = 20  # May change as needed

    user_points.add_points(quiz_bonus_points)       ## Award the user with the bonus points depending on correct answers

    return JsonResponse({'message': f'Quiz completed! {quiz_bonus_points} points awarded.'})

@login_required
def user_achievements(request):             ## Function to display the user's achievements
    achievements = Achievement.objects.filter(users_earned=request.user)
    data = [{'name': ach.name, 'description': ach.description} for ach in achievements]
    
    return JsonResponse({'achievements': data})


@login_required
@csrf_exempt
def complete_task(request, task_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            day_number = data.get("day_number")  # Expecting 1-indexed day

            print("Received day_number:", day_number)  # Debugging

            task = get_object_or_404(StudyTask, id=task_id)
            breakdown = task.daily_breakdown

            index = int(day_number) - 1
            if 0 <= index < len(breakdown):
                breakdown[index]['completed'] = True
                task.daily_breakdown = breakdown
                task.save()

                # Update progress
                completed_days = sum(1 for day in breakdown if day.get("completed"))
                total_days = len(breakdown)
                progress = round((completed_days / total_days) * 100)
                task.progress = progress
                task.save()

                # Award points
                user_points, _ = UserPoints.objects.get_or_create(user=task.user)
                user_points.add_points(10)  # Award 10 XP for completing a task

                # Update streak
                user_streak, _ = UserStreak.objects.get_or_create(user=task.user)
                user_streak.update_streak(date.today())

                return JsonResponse({
                    'success': True,
                    'xp': user_points.points,
                    'streak': user_streak.current_streak,
                    'progress': progress
                })
            else:
                return JsonResponse({'success': False, 'error': 'Invalid day number'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)