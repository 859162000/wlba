from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
class ShumiProfile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)

    resource_owner_token = models.CharField(max_length=50, blank=True, default='')
    resource_owner_secret = models.CharField(max_length=50, blank=True, default='')

    access_token = models.CharField(max_length=50, blank=True, default='')

    def __unicode__(self):
        return "%s's access_token is %s" % (self.user.username, self.access_token)

    def authorized(self):
        if self.access_token != '':
            return False
        return True