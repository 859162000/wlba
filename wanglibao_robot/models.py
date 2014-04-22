from datetime import datetime, timedelta
from django.db import models
from django.utils import timezone


class ScrawlItem(models.Model):
    name = models.CharField(max_length=128, blank=True, db_index=True)
    issuer_name = models.CharField(max_length=32, blank=True, db_index=True)
    last_updated = models.DateTimeField(default=timezone.now() - timedelta(weeks=10))
    source_url = models.TextField(blank=True)
    type = models.CharField(max_length=12, blank=True)
    item_id = models.IntegerField(default=0, db_index=True)

    def __unicode__(self):
        return u'type: %s issuer: %s name: %s' % (self.type, self.issuer_name, self.name)
