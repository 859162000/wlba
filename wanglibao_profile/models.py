from django.contrib.auth import get_user_model
from django.db import models


class WanglibaoUserProfile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)

    phone = models.CharField(verbose_name="Mobile phone number", max_length=64, default="")
    phone_verified = models.BooleanField(verbose_name="Mobile phone verified", default=False)

    identity_type = models.CharField(verbose_name="Identity type: id, passport etc", max_length=10, default="id", choices=(
        ('id', 'id card number'),
        ('passport', 'passport number'),
        ('military', 'military id')
    ))
    identity = models.CharField(verbose_name="Identity", max_length=128, default="")

    risk_level = models.PositiveIntegerField(verbose_name="How risky the user is, 1..5", default=2)
    investment_asset = models.IntegerField(verbose_name="How many money", default=0)
    total_asset = models.IntegerField(verbose_name="Total asset", default=0)

    def __unicode__(self):
        return "%s phone: %s" % (self.user.username, self.phone)


class PhoneValidateCode(models.Model):
    """
    The model to store phone number and its validate code

    phone: 13888888888
    validate_code: 4512
    validate_type: registration? password-reset? You name it. But the type should be checked to make sure it is
                    the code you triggered
    is_validated: True | False
    last_send_time: 2013-10-11 11:00:00
    code_send_count: How many times the phone received a validate code
    data: Can store arbitrary data here, may be some notes
    """
    phone = models.CharField(verbose_name="Mobile phone number", max_length=64, unique=True)
    validate_code = models.CharField(verbose_name="Validate code", max_length=6)
    validate_type = models.CharField(max_length=64)
    is_validated = models.BooleanField(default=False)
    last_send_time = models.DateTimeField()
    code_send_count = models.IntegerField(default=0)
    data = models.TextField(default="")

    def __unicode__(self):
        return "Phone: %s Code: %s Send: %s" % (self.phone, self.validate_code, self.last_send_time.__str__())