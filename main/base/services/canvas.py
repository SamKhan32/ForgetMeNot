import requests
from datetime import datetime
from base.models import Assignment, CanvasIntegration
from django.utils.dateparse import parse_datetime
from django.utils.timezone import make_aware

def fetch_canvas_assignments(user):
    integration = CanvasIntegration.objects.get(user=user)
    token = integration.access_token
    base_url = integration.canvas_url.rstrip('/')

    headers = {"Authorization": f"Bearer {token}"}
    url = f"{base_url}/api/v1/users/self/upcoming_events"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Canvas API request failed")

    data = response.json()
    added_count = 0

    for item in data:
        if "assignment" in item:
            a = item["assignment"]
            title = a.get("name", "Untitled")
            course = item.get("context_name", "Unknown Course")
            description = a.get("description", "")
            due = a.get("due_at")
            due_date = make_aware(parse_datetime(due)) if due else None

            # Check if assignment already exists
            exists = Assignment.objects.filter(
                user=user,
                title=title,
                course_name=course,
                due_date=due_date
            ).exists()

            if not exists:
                Assignment.objects.create(
                    user=user,
                    title=title,
                    course_name=course,
                    description=description,
                    due_date=due_date
                )
                added_count += 1

    return added_count