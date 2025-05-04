from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('restore/', views.restorePage, name='restore'),
    path('logout/', views.logoutUser, name='logout'),  
    path('settings/', views.settingsPage, name='settings'),  
    path('leaderboard/', views.leaderboardPage, name='leaderboard'),
    path('', views.home, name='home'),
]