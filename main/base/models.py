from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model



# Create your models here.
class Event(models.Model):
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
    # a event could have a number of tasks associated with it
class Task(models.Model):
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
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reminder_time = models.DateTimeField()
    sent = models.BooleanField(default=False)  # Track if reminder has been sent
    notification_method = models.CharField(max_length=50, choices=[('email', 'Email'), ('sms', 'SMS')])  # Method of notification

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    timezone = models.CharField(max_length=50, default="EST") 
    birthdate = models.DateField(null=True, blank=True)  # Custom field for birthdate, we could celebrate a birthday lol
    canvas_url = models.URLField(null=True, blank=True)  # Custom field for Canvas URL
    canvas_token = models.CharField(max_length=255, null=True, blank=True)  # Custom field for Canvas token
    # for use with canvas
class CanvasIntegration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    canvas_url = models.URLField()
    access_token = models.CharField(max_length=255)
    last_synced = models.DateTimeField(null=True, blank=True)
    # for use with slack
class SlackIntegration(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    slack_user_id = models.CharField(max_length=50)
    bot_access_token = models.CharField(max_length=255)
    channel_id = models.CharField(max_length=50, null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)

# Create your models here.
class Assignment(models.Model):
    User = get_user_model()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # NEW FIELD
    title = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course_name = models.CharField(max_length=200)
    due_date = models.DateTimeField()


    def __str__(self):
        return f"{self.course_name}, {self.title} due {self.due_date}"
    
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomUser)
def create_canvas_integration(sender, instance, created, **kwargs):
    if created:
        CanvasIntegration.objects.create(user=instance)