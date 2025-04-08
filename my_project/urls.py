from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from study_planner import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),                ## Admin url
    
    path('', views.home, name='home'),              ## Home url
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),          ## Login url
    path('accounts/signup/', views.signup, name='signup'),                                                  ## Signup url
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),               ## Logout url
    path('past_study_plans/', views.past_study_plans, name='past_study_plans'),                             ## Past study plans url
    path("study_task/<int:task_id>/", views.study_task_detail, name="study_task_detail"),                   ## Study task detail url
<<<<<<< HEAD
    path('delete_study_plan/<int:task_id>/', views.delete_study_plan, name='delete_study_plan'),                     ## Delete study plan url

    # Gamification elements
    path("update_streak/", views.update_streak, name="update_streak"),                                      ## Update study streak
    path("award_points/", views.award_points, name="award_points"),                                         ## Award points for completing study tasks
    path("complete_quiz/", views.complete_quiz, name="complete_quiz"),                                      ## Award points for quiz completion
    path("user_achievements/", views.user_achievements, name="user_achievements"),     
    path("complete-task/<int:task_id>/", views.complete_task, name="complete_task"),
=======
    path('delete_study_plan/<int:plan_id>/', views.delete_study_plan, name='delete_study_plan'),
>>>>>>> 8e62d44c66419c301da29236cc7c25fcf0144712
]
