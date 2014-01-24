from django.db import models
from django.utils.datetime_safe import datetime
from trust.models import Trust


class HotTrust(models.Model):
    trust = models.OneToOneField(Trust)
    hot_score = models.IntegerField(help_text="How hot is this")
    added = models.DateTimeField(help_text="When this guy appear in hot list",
                                 default=datetime.now,
                                 null=True)

    def __unicode__(self):
        return u'%s score: %d' % (self.trust.name, self.hot_score)
