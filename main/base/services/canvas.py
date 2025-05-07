import requests
from base.models import Assignment
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware
from collections import defaultdict


def _normalize_datetime(dt_str):
    """
    Parse an ISO string into an aware datetime.
    If the parsed datetime is naive, make it timezone aware.
    """
    if not dt_str:
        return None
    dt = parse_datetime(dt_str)
    if dt is None:
        return None
    # If dt is naive (no tzinfo), assume default timezone and make aware
    if dt.tzinfo is None:
        dt = make_aware(dt)
    return dt


def fetch_canvas_assignments(user):
    """
    Fetches upcoming Canvas assignments for the given user and stores any new ones in the database.
    Returns the count of newly added assignments.
    """
    token = user.canvas_token
    base_url = (user.canvas_url or "").rstrip('/')
    if not base_url or not token:
        raise Exception("Canvas URL or token not set for user")
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/api/v1/users/self/upcoming_events"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Canvas API request failed with status {response.status_code}")

    data = response.json()
    added_count = 0

    for item in data:
        if "assignment" not in item:
            continue
        a = item["assignment"]
        title = a.get("name", "Untitled")
        course = item.get("context_name", "Unknown Course")
        description = a.get("description", "")
        due_dt = _normalize_datetime(a.get("due_at"))

        exists = Assignment.objects.filter(
            user=user,
            title=title,
            course_name=course,
            due_date=due_dt
        ).exists()

        if not exists:
            Assignment.objects.create(
                user=user,
                title=title,
                course_name=course,
                description=description,
                due_date=due_dt
            )
            added_count += 1

    return added_count


def fetch_assignments_per_day(user):
    """
    Returns a dict mapping each due-date (date) to the count of upcoming Canvas assignments due on that date.
    """
    token = user.canvas_token
    base_url = (user.canvas_url or "").rstrip('/')
    if not base_url or not token:
        raise Exception("Canvas URL or token not set for user")
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/api/v1/users/self/upcoming_events"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Canvas API request failed with status {response.status_code}")

    data = response.json()
    counts = defaultdict(int)

    for item in data:
        if "assignment" not in item:
            continue
        a = item["assignment"]
        due_dt = _normalize_datetime(a.get("due_at"))
        if due_dt:
            counts[due_dt.date()] += 1

    return dict(counts)
