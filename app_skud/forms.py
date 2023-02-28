from django import forms

from app_controller.models import Controller


class CheckpointSelect(forms.Select):
    def create_option(
        self, name, value, label, selected, index, subindex=None, attrs=None
    ):
        option = super().create_option(
            name, value, label, selected, index, subindex, attrs
        )
        if value:
            option["attrs"]["checkpoint"] = value.instance
        return option


class MonitorCheckAccessModelForm(forms.ModelForm):
    class Meta:
        model = Controller
        fields = [
            "checkpoint",
        ]
        widgets = {"checkpoint": CheckpointSelect}
