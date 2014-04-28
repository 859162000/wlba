from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
class ShumiProfile(models.Model):
    user = models.OneToOneField(get_user_model(), primary_key=True)
    #store resource owner and secret.
    #before oauth provider grant the access key, the authorized field should be False.
    resource_owner_key = models.CharField(max_length=50, blank=True, default='')
    resource_owner_secret = models.CharField(max_length=50, blank=True, default='')
    #oauth verifier used for exchange(grant) access token.
    oauth_verifier = models.CharField(max_length=50, blank=True, default='')
    authorized = models.BooleanField(default=False)


    def __unicode__(self):
        return "%s's authorized status is %s" % (self.user.username, self.authorized)
