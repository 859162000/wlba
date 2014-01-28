from django.contrib.auth import get_user_model
from django.db import models


class PreOrder(models.Model):
    product_name = models.CharField(max_length=256)
    product_type = models.CharField(max_length=256, choices=(
        ('trust', 'trust'),
        ('financing', 'financing'),
        ('fund', 'fund'),
    ))
    product_url = models.TextField(default='')
    user_name = models.CharField(max_length=64)
    phone = models.CharField(max_length=64)
    user = models.ForeignKey(get_user_model(), blank=True, null=True)
    processed = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s %s %s" % (self.phone, self.user_name, self.product_name)
