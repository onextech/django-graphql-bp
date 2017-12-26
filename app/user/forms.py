from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email']


class UpdateUserForm(forms.ModelForm):
    username = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['email','first_name', 'is_active', 'last_name', 'username']

