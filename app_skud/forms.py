from django.forms import ModelForm, DateField, ModelChoiceField
from django import forms

from .models import MonitorEvents, Staffs, Department
from .utilities import validation_and_formatting_of_pass_number_form


class MonitorEventsModelForm(ModelForm):
    staff = ModelChoiceField(queryset=Staffs.objects.all(), label='ФИО сотрудника')
    departament = ModelChoiceField(queryset=Department.objects.all(), label='Департамент')
    start_date = DateField(widget=forms.SelectDateWidget(), label='Начальная дата')
    end_date = DateField(widget=forms.SelectDateWidget(), label='Конечная дата')
    
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
    microscope = forms.BooleanField(label='Отправить сигнал в Microscope', help_text='Если выбран данный параметр, фото и учетные данные сотрудника будут сохранены/изменены/удалены в системе распознования лиц', initial=True)
    def __init__(self, *args, **kwargs):
        super(StaffsModelForm, self).__init__(*args, **kwargs)
        self.fields['microscope'].required = False

    def clean(self):
        cleaned_data = super(StaffsModelForm, self).clean()
        microscope = cleaned_data.get("microscope")
        employee_photo = cleaned_data.get('employee_photo')
        pass_number = cleaned_data.get('pass_number')
        pass_number = validation_and_formatting_of_pass_number_form(input_pass_num=pass_number)
        if microscope and employee_photo == None:
            self.add_error('employee_photo', error='Для отправки фото в базу распознания лиц нужна фотография.')
        if not pass_number:
            self.add_error('pass_number', error='Не корректный номер пропуска.')

    class Meta:
        model = Staffs
        # required = False
        fields = '__all__'
        

class MonitorEventsTabelModelForm(ModelForm):
    staff = ModelChoiceField(queryset=Staffs.objects.all(), label='ФИО сотрудника')
    start_date = DateField(widget=forms.SelectDateWidget(), label='Начальная дата')
    end_date = DateField(widget=forms.SelectDateWidget(), label='Конечная дата')
    
    class Meta:
        model = MonitorEvents
        fields = [
            'staff',
        ]
        
    def __init__(self, *args, **kwargs):
        super(MonitorEventsTabelModelForm, self).__init__(*args, **kwargs)
        self.fields['staff'].required = False