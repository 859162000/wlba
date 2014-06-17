from captcha.fields import CaptchaField
import django.forms as forms


class PurchaseForm(forms.Form):
    amount = forms.IntegerField()
    captcha = CaptchaField()
