from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.conf import settings

from .forms import CustomUserCreationForm, CanvasTokenForm
from .services.canvas import fetch_canvas_assignments
from .models import Assignment

import datetime
import calendar
import random
from zoneinfo import ZoneInfo

User = get_user_model()

TZ_MAP = {
    'EST': 'America/New_York',
    'CST': 'America/Chicago',
    'MST': 'America/Denver',
    'PST': 'America/Los_Angeles',
}

def loginPage(request):
    if request.user.is_authenticated:
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

    return render(request, 'base/register.html', {'form': form})

def restorePage(request):
    return render(request, 'base/restore.html', {})

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

@login_required(login_url='login')
def home(request):
    user = request.user
    today = datetime.date.today()
    year = today.year
    requested_month = request.GET.get('month')

    if requested_month:
        try:
            month = list(calendar.month_name).index(requested_month)
            if month == 0:
                raise ValueError
        except ValueError:
            month = today.month
    else:
        month = today.month

    _, num_days = calendar.monthrange(year, month)
    current_day = today.day

    prev_month, prev_year = (12, year-1) if month==1 else (month-1, year)
    next_month, next_year = (1, year+1)  if month==12 else (month+1, year)

    tz_name = TZ_MAP.get(getattr(user, 'timezone', None), settings.TIME_ZONE)
    user_zone = ZoneInfo(tz_name)

    local_start = datetime.datetime(year, month, 1, tzinfo=user_zone)
    local_end = datetime.datetime(year+1, 1, 1, tzinfo=user_zone) if month == 12 else datetime.datetime(year, month+1, 1, tzinfo=user_zone)

    utc = ZoneInfo('UTC')
    start_utc = local_start.astimezone(utc)
    end_utc   = local_end.astimezone(utc)

    qs = Assignment.objects.filter(user=user, due_date__gte=start_utc, due_date__lt=end_utc)

    counts = {d: 0 for d in range(1, num_days + 1)}
    assignments_by_day = {d: [] for d in range(1, num_days + 1)}

    for a in qs:
        local_dt = a.due_date.astimezone(user_zone)
        a.local_due_date = local_dt
        counts[local_dt.day] += 1
        assignments_by_day[local_dt.day].append(a)

    day_objects = [
        {"day": d, "count": counts[d], "assignments": assignments_by_day[d]}
        for d in range(1, num_days + 1)
    ]

    context = {
        "day_objects":   day_objects,
        "current_day":   current_day,
        "month":         calendar.month_name[month],
        "month_num":     month,
        "year":          year,
        "prev_month":    calendar.month_name[prev_month],
        "next_month":    calendar.month_name[next_month],
        "prev_year":     prev_year,
        "next_year":     next_year,
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

    return render(request, 'base/settings.html', {'user': user})

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
            user.canvas_url = form.cleaned_data['canvas_url']
            user.canvas_token = form.cleaned_data['canvas_token']
            user.save()
            messages.success(request, "Canvas integration saved!")
            return redirect('connect')
    else:
        form = CanvasTokenForm(initial={
            'canvas_url': user.canvas_url,
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

@login_required
def reset_canvas_token(request):
    user = request.user
    user.canvas_url = ""
    user.canvas_token = ""
    user.save()
    Assignment.objects.filter(user=user).delete()
    messages.success(request, "Canvas token removed!")
    return redirect("connect")
