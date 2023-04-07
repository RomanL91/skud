from django.forms import ModelForm, DateField, ModelChoiceField
from django import forms

from .models import MonitorEvents, Staffs, Department


class MonitorEventsModelForm(ModelForm):
    staff = ModelChoiceField(queryset=Staffs.objects.all())
    departament = ModelChoiceField(queryset=Department.objects.all())
    start_date = DateField(widget=forms.SelectDateWidget())
    end_date = DateField(widget=forms.SelectDateWidget())
    class Meta:
        model = MonitorEvents
        fields = [
            'staff',
            'checkpoint',
        ]

    def __init__(self, *args, **kwargs):
        super(MonitorEventsModelForm, self).__init__(*args, **kwargs)
        self.fields['staff'].required = False
        self.fields['departament'].required = False
