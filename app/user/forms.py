from django.conf import settings
from django.contrib.auth import forms as django_auth_forms, update_session_auth_hash, get_user_model
from django import forms


class ChangePasswordForm(django_auth_forms.PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.fields['new_password1'].user = self.user
        self.fields['old_password'].widget.attrs['placeholder'] = ''
        self.fields['new_password1'].widget.attrs['placeholder'] = ''
        del self.fields['new_password2']


def logout_on_password_change(request, user):
    if (update_session_auth_hash is not None and
            not settings.LOGOUT_ON_PASSWORD_CHANGE):
        update_session_auth_hash(request, user)


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email', 'password']

    def clean_email(self) -> str:
        return self.cleaned_data['email'].lower()

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        # Always save password with hash using Django's built-in
        # `set_password` method. Otherwise, saved password will be raw.
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user
