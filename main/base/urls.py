from django.urls import path
from . import views
from base.views import sync_canvas_simple, reset_canvas_token

urlpatterns = [
    path('/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('restore/', views.restorePage, name='restore'),
    path('logout/', views.logoutUser, name='logout'),  
    path('settings/', views.settingsPage, name='settings'),  
    path('leaderboard/', views.leaderboardPage, name='leaderboard'),
    path('', views.home, name='home'),
    path('connect/',views.connectPage, name='connect'),
    path('sync_canvas/', sync_canvas_simple, name='sync_canvas'),
    path("reset-canvas/", reset_canvas_token, name="reset_canvas"),
]