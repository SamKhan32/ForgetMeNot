import requests  # HTTP client for making API calls to Canvas
from base.models import Assignment  # Import the Assignment model to store fetched data
from django.utils.dateparse import parse_datetime  # Parses ISO datetime strings
from django.utils.timezone import make_aware, localtime  # For handling timezone-aware datetimes
from collections import defaultdict  # For counting assignments per date


def _normalize_datetime(dt_str):
    """
    Convert an ISO 8601 datetime string into a timezone-aware local datetime object.
    """
    if not dt_str:
        return None

    dt = parse_datetime(dt_str)  # Parse the string into a datetime object
    if dt is None:
        return None

    # If the datetime is naive (no timezone), make it aware using default timezone
    if dt.tzinfo is None:
        dt = make_aware(dt)

    # Convert UTC time to the server's local time zone
    dt = localtime(dt)
    return dt


def fetch_canvas_assignments(user):
    """
    Syncs upcoming Canvas assignments for the given user.
    Stores new assignments in the database and returns a count of how many were added.
    """
    # Get user's Canvas credentials
    token = user.canvas_token
    base_url = (user.canvas_url or "").rstrip('/')

    # Check if credentials are valid
    if not base_url or not token:
        raise Exception("Canvas URL or token not set for user")

    # Ensure the base URL starts with a valid scheme
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url

    # Set the authorization header and endpoint
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/api/v1/users/self/upcoming_events"

    # Make the API request
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Canvas API request failed with status {response.status_code}")

    data = response.json()  # Parse JSON response
    added_count = 0  # Track number of new assignments added

    for item in data:
        if "assignment" not in item:
            continue  # Skip non-assignment events

        a = item["assignment"]
        title = a.get("name", "Untitled")
        course = item.get("context_name", "Unknown Course")
        description = a.get("description", "")
        due_dt = _normalize_datetime(a.get("due_at"))  # Normalize due date

        # Check for duplicate based on title, course, date, and user
        exists = Assignment.objects.filter(
            user=user,
            title=title,
            course_name=course,
            due_date=due_dt
        ).exists()

        # If assignment doesn't exist yet, add it
        if not exists:
            Assignment.objects.create(
                user=user,
                title=title,
                course_name=course,
                description=description,
                due_date=due_dt
            )
            added_count += 1

    return added_count  # Return how many new assignments were saved


def fetch_assignments_per_day(user):
    """
    Returns a dictionary mapping each due date (date) to a count of assignments due that day.
    Used to populate the calendar view.
    """
    # Get user's Canvas credentials
    token = user.canvas_token
    base_url = (user.canvas_url or "").rstrip('/')

    # Validate credentials
    if not base_url or not token:
        raise Exception("Canvas URL or token not set for user")

    # Ensure valid URL scheme
    if not base_url.startswith(('http://', 'https://')):
        base_url = 'https://' + base_url

    # Make API call
    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/api/v1/users/self/upcoming_events"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Canvas API request failed with status {response.status_code}")

    data = response.json()  # Parse response
    counts = defaultdict(int)  # Dictionary to count assignments per date

    # Process each item and increment date counters
    for item in data:
        if "assignment" not in item:
            continue
        a = item["assignment"]
        due_dt = _normalize_datetime(a.get("due_at"))
        if due_dt:
            counts[due_dt.date()] += 1  # Increment count for the specific date

    return dict(counts)  # Return the date-to-count mapping
