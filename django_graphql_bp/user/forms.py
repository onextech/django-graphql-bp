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
    email = forms.EmailField(required=False)
    is_active = forms.BooleanField(required=False)
    name = forms.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'is_active', 'name']

    def clean(self) -> dict:
        cleaned_data = super(UpdateUserForm, self).clean()

        for field in self.fields:
            if field not in self.data.keys():
                cleaned_data[field] = getattr(self.instance, field)

        return cleaned_data


