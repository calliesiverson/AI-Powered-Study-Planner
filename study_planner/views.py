from django.shortcuts import render
from .models import StudyTask
from .utils import generate_study_plan

def home(request):
    tasks = StudyTask.objects.all()  # Fetch tasks from the database
    study_plan = None  # Default to None

    if request.method == "POST":
        task_title = request.POST.get("task_title")  # Get input from user
        if task_title:  # Ensure task title isn't empty
            study_plan = generate_study_plan(task_title, list(tasks))  # Generate study plan

    return render(request, "home.html", {"tasks": tasks, "study_plan": study_plan})
    
# def study_plan_view(request, task_id):
#     plan = generate_study_plan(task_id)
#     return JsonResponse({"study_plan": plan})
