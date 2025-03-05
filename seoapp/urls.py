from django.urls import path 
from . import views 

urlpatterns = [
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('plans/', views.plans_view, name='plans'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/settings/', views.update_settings, name='update_settings'),
    path('signin/', views.signin_view, name='signin'),
    path('signup/', views.signup_view, name='signup'),
    path('add_project/', views.add_project, name='add_project'),
    path('project/<int:id>/', views.view_project, name='view_project'),
    path('reports/', views.reports_view, name='reports'),
    path('change_plan/<str:plan>/', views.change_plan, name='change_plan'),  # Add this line
]
