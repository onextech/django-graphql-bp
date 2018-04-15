from django_graphql_bp.graphql.forms import UpdateForm
from django_graphql_bp.user.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm


class CreateUserForm(UserCreationForm):
    class Meta:
        fields = [
            'email'
        ]
        model = User

    def clean_email(self) -> str:
        email = self.cleaned_data.get('email')
        self.instance.username = email
        return email


class UpdateUserForm(UpdateForm):
    class Meta:
        model = User
        fields = [
            'email',
            'is_active',
            'name'
        ]

