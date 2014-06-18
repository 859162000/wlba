from captcha.fields import CaptchaField
import django.forms as forms
from wanglibao_p2p.models import P2PProduct


class PurchaseForm(forms.Form):
    product = forms.ModelChoiceField(queryset=P2PProduct.objects.all(), widget=forms.HiddenInput())
    amount = forms.IntegerField()
    captcha = CaptchaField()
