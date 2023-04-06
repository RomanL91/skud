from django.forms import ModelForm, DateField
from django import forms

from .models import MonitorEvents, Staffs


class MonitorEventsModelForm(ModelForm):
    start_date = DateField(widget=forms.SelectDateWidget())
    end_date = DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = MonitorEvents
        fields = [
            'staff',
            'checkpoint',
        ]

class StaffsModelForm(ModelForm):
    class Meta:
        model = Staffs
        required = False
        fields = [
            'last_name',
            'first_name',
            'phone_number',
            'pass_number',
        ]
    def __init__(self, *args, **kwargs):
        super(StaffsModelForm, self).__init__(*args, **kwargs)
        self.fields['last_name'].required = False
        self.fields['first_name'].required = False
        self.fields['phone_number'].required = False
        self.fields['pass_number'].required = False
        