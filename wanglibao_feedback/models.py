# encoding:utf-8
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.html import format_html

class Feedback(models.Model):
    content = models.TextField(blank=True, help_text=u'反馈')
    created_at = models.DateTimeField(default=timezone.now, blank=True, help_text=u'创建时间')
    created_by = models.ForeignKey(get_user_model(), blank=True, null=True, help_text=u'意见提交人')

    def one_line_created_at(self):
        return format_html('<div style="width: 100px;">{}</div>', self.created_at.strftime("%Y-%m-%d %H:%M"))

    def __unicode__(self):
        return self.content[:15]
