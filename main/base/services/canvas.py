import requests
from datetime import datetime
from base.models import Assignment, CanvasIntegration
from django.utils.dateparse import parse_datetime

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
    assignments = []

    for item in data:
        if "assignment" in item:
            a = item["assignment"]
            assignment = Assignment(
                title=a.get("name", "Untitled"),
                course_name=item.get("context_name", "Unknown Course"),
                description=a.get("description", ""),
                due_date=parse_datetime(a.get("due_at"))
            )
            assignments.append(assignment)

    return assignments