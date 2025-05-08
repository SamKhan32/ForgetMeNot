from django.db import models  # Import base model class
from django.conf import settings  # Access project settings like AUTH_USER_MODEL
from django.contrib.auth.models import AbstractUser  # For custom user model
from django.contrib.auth import get_user_model  # Dynamically get the user model

# ---------------------- Event and Task Management Models ----------------------

class Event(models.Model):
    """
    Represents a user's event with a name, description, and due date.
    Can be linked to multiple tasks and reminders.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    due_date = models.DateTimeField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    def mark_complete(self):
        self.is_completed = True
        self.save()

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Represents a subtask of an Event.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tasks')
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)

    def mark_complete(self):
        self.is_completed = True
        self.save()

    def __str__(self):
        return f"{self.name} (for {self.event.name})"


class Reminder(models.Model):
    """
    Represents a reminder linked to an Event and User, with notification tracking.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    sent = models.BooleanField(default=False)
    notification_method = models.CharField(
        max_length=50,
        choices=[('email', 'Email'), ('sms', 'SMS')]
    )

# ---------------------- Custom User Model ----------------------

class CustomUser(AbstractUser):
    """
    Extends the default user with extra fields for profile and Canvas integration.
    """
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    timezone = models.CharField(max_length=50, default="EST")
    birthdate = models.DateField(null=True, blank=True)
    canvas_url = models.URLField(null=True, blank=True)
    canvas_token = models.CharField(max_length=255, null=True, blank=True)

# ---------------------- Integration Models ----------------------

class CanvasIntegration(models.Model):
    """
    Represents a user's Canvas integration credentials and sync status.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    canvas_url = models.URLField()
    access_token = models.CharField(max_length=255)
    last_synced = models.DateTimeField(null=True, blank=True)


class SlackIntegration(models.Model):
    """
    Represents Slack bot configuration for a user.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slack_user_id = models.CharField(max_length=50)
    bot_access_token = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=50, null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)

# ---------------------- Assignment Model ----------------------

class Assignment(models.Model):
    """
    Represents a user's academic assignment with details like title, course, and due date.
    """
    User = get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course_name = models.CharField(max_length=200)
    due_date = models.DateTimeField()

    def __str__(self):
        return f"{self.course_name}, {self.title} due {self.due_date}"

# ---------------------- Signal for CanvasIntegration auto-creation ----------------------

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_canvas_integration(sender, instance, created, **kwargs):
    """
    Automatically creates a CanvasIntegration object when a new CustomUser is created.
    """
    if created:
        CanvasIntegration.objects.create(user=instance)
