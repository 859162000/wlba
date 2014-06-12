from django.contrib.auth import get_user_model
from django.db import models


class PayInfo(models.Model):
    type = models.CharField(help_text=u'', max_length=5)
    amount = models.FloatField()
    user = models.ForeignKey(get_user_model())
