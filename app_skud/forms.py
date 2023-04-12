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
        
