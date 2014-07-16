from django import forms


class PreOrderP2PForm(forms.Form):
    name = forms.CharField(max_length=32)
    phone = forms.CharField(max_length=32)
    amount = forms.IntegerField(min_value=0)
