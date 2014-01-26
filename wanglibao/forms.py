from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.TextInput(attrs={'class': 'login-input'})
    password = forms.PasswordInput(attrs={'class': 'login-input'})

