# encoding:utf8
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from jsonfield import JSONField


class Order(models.Model):
    """
    The main order model
    """
    STATUS_NEW = u'新建'

    type = models.CharField(max_length=64, verbose_name=u'订单类型')
    status = models.CharField(max_length=64, verbose_name=u'订单状态', default=STATUS_NEW)

    created_at = models.DateTimeField(default=timezone.now, verbose_name=u'订单创建时间')

    # Field for storing extra data
    extra_data = JSONField(blank=True)

    def __unicode__(self):
        return u"%s %s %s"


class OrderNote(models.Model):
    order = models.ForeignKey(Order, related_name='notes', verbose_name=u'订单')
    user = models.ForeignKey(get_user_model(), null=True, verbose_name=u'用户')

    # System generated note can't be edited
    SYSTEM = 'System'

    type = models.CharField(max_length=64, verbose_name=u'流水类型')
    message = models.TextField(u'流水信息')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    extra_data = JSONField(blank=True)

    editable_lifetime = 300

    def __unicode__(self):
        return u'%s (%s)' % (self.message[:50], self.user)

    def is_editable(self):
        if self.note_type == self.SYSTEM:
            return False
        delta = timezone.now() - self.updated_at
        return delta.seconds < self.editable_lifetime
