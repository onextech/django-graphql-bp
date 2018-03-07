from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.forms.fields import FileField
from django.forms.models import ModelMultipleChoiceField


class UpdateForm(forms.ModelForm):
    def _clean_fields(self):
        for name, field in self.fields.items():
            self.validate_field(field, name, self.get_field_value(field, name))

    def get_field_value(self, field, name: str):
        if field.disabled:
            value = self.get_initial_for_field(field, name)
        else:
            value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))

            if not value:
                if isinstance(field, ModelMultipleChoiceField):
                    # if value is belongs to m2m relation field
                    if not self.instance.pk:
                        value = []
                    else:
                        value = getattr(self.instance, name)
                        value = value.all().values_list('pk', flat=True)
                else:
                    value = getattr(self.instance, name)

                if isinstance(value, models.Model):
                    value = value.pk

        return value

    def validate_field(self, field, name: str, value):
        try:
            if isinstance(field, FileField):
                initial = self.get_initial_for_field(field, name)
                value = field.clean(value, initial)
            else:
                value = field.clean(value)

            self.cleaned_data[name] = value

            if hasattr(self, 'clean_%s' % name):
                value = getattr(self, 'clean_%s' % name)()
                self.cleaned_data[name] = value
        except ValidationError as e:
            self.add_error(name, e)
