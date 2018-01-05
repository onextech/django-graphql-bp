from django_graphql_bp.user.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        self.instance.username = email
        return email


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'is_active', 'name']


