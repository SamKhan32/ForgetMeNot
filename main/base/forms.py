from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .models import CanvasIntegration
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
class CanvasTokenForm(forms.Form):
    canvas_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'placeholder': 'Canvas URL',
            'class': 'form-control'
        }),
        required=True
    )
    canvas_token = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'placeholder': 'Canvas API Token',
            'class': 'form-control'
        }),
        required=True
    )