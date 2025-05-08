from django import forms  # Import Django's form utilities
from django.contrib.auth.forms import UserCreationForm  # Built-in form for user registration
from .models import CustomUser, CanvasIntegration  # Import models from the current app

# Timezone choices for the user to select during registration
TIMEZONE_CHOICES = [
    ('EST', 'Eastern Standard Time'),
    ('CST', 'Central Standard Time'),
    ('MST', 'Mountain Standard Time'),
    ('PST', 'Pacific Standard Time'),
]

class CustomUserCreationForm(UserCreationForm):
    """
    A custom user creation form that includes additional fields: birthdate and timezone.
    Inherits from Django's built-in UserCreationForm.
    """
    birthdate = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})  # HTML5 date picker
    )

    timezone = forms.ChoiceField(
        choices=TIMEZONE_CHOICES,  # Dropdown list of timezones
        required=True
    )

    class Meta:
        model = CustomUser  # Use our custom user model
        fields = ['username', 'email', 'birthdate', 'timezone', 'password1', 'password2']  # Form fields to render

class CanvasTokenForm(forms.Form):
    """
    A form used to collect Canvas LMS integration data (URL and access token).
    """
    canvas_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'Canvas URL',  # Placeholder example: https://school.instructure.com
            'class': 'form-control'  # Bootstrap-compatible styling
        }),
        required=True
    )

    canvas_token = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Canvas API Token',  # Placeholder text to guide users
            'class': 'form-control'
        }),
        required=True
    )
