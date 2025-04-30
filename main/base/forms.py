from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
# Define your timezone choices
TIMEZONE_CHOICES = [
    ('EST', 'Eastern Standard Time'),
    ('CST', 'Central Standard Time'),
    ('MST', 'Mountain Standard Time'),
    ('PST', 'Pacific Standard Time'),
]
class CustomUserCreationForm(UserCreationForm):
    
    birthdate = forms.DateField(
    required=False,
    widget=forms.DateInput(attrs={'type': 'date'})
    )
    timezone = forms.ChoiceField(
    choices=TIMEZONE_CHOICES,
    required=True
    )
    class Meta:
        model = CustomUser

        fields = ['username', 'email', 'birthdate', 'timezone', 'password1', 'password2']