from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from study_planner import views
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),

    # Update these to remove 'accounts/' prefix unless needed
    path('accounts/login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('accounts/signup/', views.signup, name='signup'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]
