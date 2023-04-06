from django import forms


class AddNumberCardsInControllerForm(forms.Form):
    card_number = forms.CharField()
