from django.db import models

#from __future__ import unicode_literals

from django.db import models

class AntiDelayCallback(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.IntegerField()
    createtime = models.IntegerField()
    updatetime = models.IntegerField()
    channel = models.CharField(max_length=32)
    status = models.IntegerField()
    device = models.CharField(max_length=1024)
    ip = models.CharField(max_length=32)
    class Meta:
        managed = False
        db_table = 'anti_delay_callback'


# Create your models here.
