# encoding:utf-8
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Feedback(models.Model):
    content = models.TextField(blank=True, help_text=u'反馈')
    created_at = models.DateTimeField(default=timezone.now, blank=True, help_text=u'创建时间')
    created_by = models.ForeignKey(get_user_model(), blank=True, null=True, help_text=u'意见提交人')

    def __unicode__(self):
        return self.content[:15]
