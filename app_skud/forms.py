from django.forms import ModelForm, DateField
from django import forms

from .models import MonitorEvents


class MonitorEventsModelForm(ModelForm):
    start_date = DateField(widget=forms.SelectDateWidget())
    end_date = DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = MonitorEvents
        fields = [
            'staff',
            'checkpoint',
        ]