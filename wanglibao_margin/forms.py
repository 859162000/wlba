# coding=utf-8

import django.forms as forms
from .models import MarginRecord


class MarginRecordForm(forms.ModelForm):
    class Meta:
        model = MarginRecord
