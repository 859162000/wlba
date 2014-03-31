from django.db import models


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