# coding=utf-8
from django.db import models
from django.utils import timezone
from django.db.models.signals import post_save


class PhoneValidateCode(models.Model):
    """
    The model to store phone number and its validate code

    phone: 13888888888
    validate_code: 4512
    validate_type: registration? password-reset? You name it. But the type should be checked to make sure it is
                    the code you triggered
    is_validated: True | False
    last_send_time: 2013-10-11 11:00:00
    code_send_count: How many times the phone received a validate code
    data: Can store arbitrary data here, may be some notes
    """
    phone = models.CharField(u'手机号码', max_length=64, unique=True)
    validate_code = models.CharField(verbose_name="Validate code", max_length=6)
    validate_type = models.CharField(max_length=64)
    is_validated = models.BooleanField(default=False)
    last_send_time = models.DateTimeField()
    code_send_count = models.IntegerField(default=0)
    vcount = models.IntegerField(u"验证次数", null=False, blank=False, default=0)
    data = models.TextField(default="")

    class Meta:
        verbose_name_plural = u'验证码'
        ordering = ['-last_send_time']

    def __unicode__(self):
        return "Phone: %s Code: %s Send: %s" % (self.phone, self.validate_code, self.last_send_time.__str__())


class ShortMessage(models.Model):
    """
    The model holds all sent short messages, it is used to do tracking on
    how many messages we send and send to whom
    """

    phones = models.TextField(u'号码')
    contents = models.TextField(u'内容')
    type = models.CharField(u'类型', max_length=8, choices=(
        (u'手动', u'手动'),
        (u'系统', u'系统')
    ), default=u'系统')
    status = models.CharField(u'结果', max_length=8, choices=(
        (u'发送中', u'发送中'),
        (u'成功', u'成功'),
        (u'失败', u'失败'),
    ), default=u'发送中')
    context = models.TextField(u'相关信息', blank=True)
    channel = models.CharField(u'短信网关', max_length=10, choices=(
        (u'慢道', u'慢道'),
        (u'亿美', u'亿美'),
    ), default=u'慢道')
    created_at = models.DateTimeField(u'发送时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u'已发送短信'
        ordering = ['-created_at']

    def __unicode__(self):
        return u'手机号：%s 内容：%s' % (self.phones, self.contents)

class RateThrottle(models.Model):
    ip = models.CharField(u'ip', max_length=24, db_index=True)
    max_count = models.IntegerField(u"最大发送次数", null=False, blank=False, default=10)
    send_count = models.IntegerField(u"已发送次数", null=False, blank=False, default=0)
    last_send_time = models.DateTimeField(default=timezone.now)


def send_manual_message(sender, instance, **kwargs):
    if instance.type == u'手动' and instance.status == u'发送中':
        #from celery.execute import send_task
        from wanglibao_sms.tasks import send_messages
        if instance.channel == u'慢道':
            channel = 1
        else:
            channel = 2
        #send_task("wanglibao_sms.tasks.send_messages", kwargs={
        #    'phones': instance.phones.split(' '),
        #    'messages': [instance.contents],
        #    'channel': channel
        #})
        send_messages.apply_async(kwargs={
            'phones': instance.phones.split(' '),
            'messages': [instance.contents],
            'channel': channel
        })
        instance.status = u'成功'
        instance.save()

post_save.connect(send_manual_message, sender=ShortMessage)
