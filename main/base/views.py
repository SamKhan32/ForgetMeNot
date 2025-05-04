from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from .services.canvas import fetch_canvas_assignments
from .models import Assignment
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.shortcuts import render
import datetime
import calendar
import random
from django.contrib.auth.models import User


User = get_user_model()

def loginPage(request):
    if request.user.is_authenticated: #if the user is already logged in
        return redirect('home')  

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password is incorrect')

    return render(request, 'base/login.html')


@login_required
def sync_canvas_assignments(request):
    try:
        assignments = fetch_canvas_assignments(request.user)
        for a in assignments:
            a.save()
        message = f"{len(assignments)} assignments synced."
    except Exception as e:
        message = str(e)

    return render(request, "sync_result.html", {"message": message})


def registerPage(request):

    form = CustomUserCreationForm()

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account was created for {username}')
            return redirect('login') 

    context = {'form': form}
    return render(request, 'base/register.html', context)

def restorePage(request):
    return render(request, 'base/restore.html', {})

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')


def home(request):
    today = datetime.date.today()
    year = today.year
    requested_month = request.GET.get('month')
    if requested_month:
        try:
            month = list(calendar.month_name).index(requested_month)
            year = today.year  # You can add year selection later if needed
        except ValueError:
            month = today.month
            year = today.year
    else:
        month = today.month
        year = today.year
    _, num_days = calendar.monthrange(year, month)

    day_list = list(range(1, num_days + 1)) 

    context = {
        'day_list' : day_list, 
        'month': calendar.month_name[month],
        'year': year,
        }
    return render(request, 'base/home.html', context)

@login_required(login_url='login')
def settingsPage(request):
    user = request.user

    if request.method == 'POST':
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()
        messages.success(request, "Settings updated successfully.")

    context = {
        'user': user
    }
    return render(request, 'base/settings.html', context)


def leaderboardPage(request):
    users = User.objects.all()
    user_scores = [(user, random.randint(1, 1000)) for user in users]
    return render(request, 'leaderboard.html', {'user_scores': user_scores})