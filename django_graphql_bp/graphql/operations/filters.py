from django import forms
from django_filters import Filter, FilterSet


class IntegerFilter(Filter):
    field_class = forms.IntegerField


class PkFilter(FilterSet):
    pk = IntegerFilter()
