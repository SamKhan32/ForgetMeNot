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
from .forms import CanvasTokenForm
from django.shortcuts import render, redirect
from .forms import CanvasTokenForm
from django.contrib.auth.decorators import login_required
from base.services.canvas import fetch_canvas_assignments
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


# base/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import datetime, calendar
from .models import Assignment

@login_required(login_url='login')
def home(request):
    today = datetime.date.today()
    year = today.year
    requested_month = request.GET.get('month')

    # Figure out which month to show
    if requested_month:
        try:
            month = list(calendar.month_name).index(requested_month)
            if month == 0:  # month_name[0] is ''
                raise ValueError
        except ValueError:
            month = today.month
    else:
        month = today.month

    # How many days in that month?
    _, num_days = calendar.monthrange(year, month)
    current_day = today.day

    # Prev / next month logic
    if month == 1:
        prev_month, prev_year = 12, year - 1
    else:
        prev_month, prev_year = month - 1, year

    if month == 12:
        next_month, next_year = 1, year + 1
    else:
        next_month, next_year = month + 1, year

    # Build a list of dicts: each day number + how many assignments
    day_objects = []
    for d in range(1, num_days + 1):
        cnt = Assignment.objects.filter(
            user=request.user,
            due_date__year=year,
            due_date__month=month,
            due_date__day=d
        ).count()
        day_objects.append({"day": d, "count": cnt})

    context = {
        "day_objects": day_objects,
        "current_day": current_day,
        "month": calendar.month_name[month],
        "month_num": month,
        "year": year,
        "prev_month": calendar.month_name[prev_month],
        "next_month": calendar.month_name[next_month],
        "prev_year": prev_year,
        "next_year": next_year,
    }
    return render(request, "base/home.html", context)

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


@login_required(login_url='login')
def connectPage(request):
    user = request.user

    if request.method == 'POST':
        form = CanvasTokenForm(request.POST)
        if form.is_valid():
            # Save into your CustomUser fields
            user.canvas_url   = form.cleaned_data['canvas_url']
            user.canvas_token = form.cleaned_data['canvas_token']
            user.save()
            messages.success(request, "Canvas integration saved!")
            return redirect('settings')
    else:
        # Pre‑fill the form with whatever’s already on the user
        form = CanvasTokenForm(initial={
            'canvas_url':   user.canvas_url,
            'canvas_token': user.canvas_token,
        })

    return render(request, 'base/connect.html', {'form': form})

@login_required
def sync_canvas_simple(request):
    if request.method == "POST":
        try:
            fetch_canvas_assignments(request.user)
            messages.success(request, "Canvas assignments updated!")
        except Exception as e:
            messages.error(request, f"Sync failed: {e}")
    return redirect("home")