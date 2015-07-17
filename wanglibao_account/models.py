#!/usr/bin/env python
# encoding: utf8

#from django.contrib.auth import get_user_model
import time
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class IdVerification(models.Model):
    """
    This is a table stores all id verification info. The verify method should
    check this table first
    """

    id_number = models.CharField(u"身份证号", max_length=128, db_index=True)
    name = models.CharField(u"姓名", max_length=32)
    is_valid = models.BooleanField(u"验证结果", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = u'实名认证记录'

    def __unicode__(self):
        return u'%s %s %d' % (self.id_number, self.name, self.is_valid)



class VerifyCounter(models.Model):
    """
    The table stores the count each user called the id verify api
    """

    user = models.OneToOneField(User)
    count = models.IntegerField(u'尝试认证次数', default=0)

    class Meta:
        verbose_name_plural = u'实名认证次数'

    def __unicode__(self):
        return u'%s: %d' % (self.user.wanglibaouserprofile.phone, self.count)


class UserPushId(models.Model):
    """
        app push table, store all the user and all the device
    """
    user = models.ForeignKey(User, null=True)
    device_type = models.CharField(max_length=20, verbose_name="设备类型", choices=(
        ("ios", "iPhone"),
        ("android", "Android")
    ))
    push_user_id = models.CharField(max_length=50, db_index=True)
    push_channel_id = models.CharField(max_length=50)

    class Meta:
        verbose_name_plural = u"推送信息"


class Binding(models.Model):
    """
        third app bind table, store bind related
    """
    user = models.ForeignKey(User)
    btype = models.CharField(max_length=10, choices=(
        ('xunlei', 'xunlei'),
        ('yiruite', 'yiruite')
    ), verbose_name=u"类型")
    bid = models.CharField(max_length=50, db_index=True, verbose_name=u"第三方用户id")
    bname = models.CharField(max_length=50, blank=True, verbose_name=u"第三方用户昵称")
    gender = models.CharField(max_length=5, choices=(
        ("m", "m"),
        ("w", "w"),
        ("n", "n"),
    ), verbose_name=u"性别", blank=True)
    isvip = models.BooleanField(default=False, verbose_name=u"是否是vip")
    extra = models.CharField(max_length=200, default="", blank=True)
    access_token = models.CharField(max_length=100, blank=True)
    refresh_token = models.CharField(max_length=100, blank=True)
    created_at = models.BigIntegerField(default=0, verbose_name=u'创建时间', blank=True)

    class Meta:
        verbose_name_plural = u'用户绑定'

message_type = (
    ("withdraw", "提现通知"),
    ("pay", "充值通知"),
    ("amortize", "项目还款"),
    ("activityintro", "活动介绍"),
    ("activity", "活动奖励"),
    ("bids", "流标通知"),
    ("purchase", "投标通知"),
    ("fullbid", "满标"), #给管理员发
    ("loaned", "投标成功"),#给持仓人发
    #("audited", "满标已审核"),
    ("public", "发给所有"),
)
def timestamp():
    return long(time.time())

class MessageText(models.Model):
    """
        store station letters(站内信内容)
    """
    mtype = models.CharField(max_length=50, verbose_name=u"消息类型", db_index=True,
        choices=message_type)
    title = models.CharField(max_length=100, verbose_name=u"消息标题")
    content = models.TextField(verbose_name=u"正文")
    created_at = models.BigIntegerField(default=timestamp, verbose_name=u"时间戳", blank=True)

    def __unicode__(self):
        return u'%s|%s' % (self.title, self.content)

    class Meta:
        verbose_name = u"站内信内容"
        verbose_name_plural = u"站内信内容"
        ordering = ['-created_at']

    @property
    def display_mtype(self):
        message_type_temp = dict(message_type)
        return message_type_temp.get(self.mtype)

    @property
    def format_time(self):
        return datetime.datetime.fromtimestamp(self.created_at)

class Message(models.Model):
    """
        store station letters relation(站内信收发关系，不存在私信功能)
    """
    target_user = models.ForeignKey(User, related_name="recive", verbose_name=u"收信方")
    message_text = models.ForeignKey(MessageText, verbose_name=u"站内信内容")
    read_status = models.BooleanField(default=False, verbose_name=u"是否查看")
    read_at = models.BigIntegerField(default=0, verbose_name=u"查看时间", blank=True)
    notice = models.BooleanField(default=True, verbose_name=u"是否通知")

    class Meta:
        verbose_name = u"站内信收发关系"
        verbose_name_plural = u"站内信收发关系"

class MessageNoticeSet(models.Model):
    """
        store everyone notice setting
    """
    user = models.ForeignKey(User, related_name="notice")
    mtype = models.CharField(max_length=50, verbose_name=u"消息类型", db_index=True,
        choices=message_type)
    notice = models.BooleanField(default=True, verbose_name=u"是否通知")


class UserAddress(models.Model):
    """
        user address setting
    """
    user = models.ForeignKey(User)
    name = models.CharField(max_length=50, verbose_name=u"收件人姓名")
    address = models.CharField(max_length=255, verbose_name=u"详细地址")
    province = models.CharField(max_length=50, verbose_name=u"省", blank=True)
    city = models.CharField(max_length=50, verbose_name=u"市", blank=True)
    area = models.CharField(max_length=50, verbose_name=u"县（区）", blank=True)
    phone_number = models.CharField(max_length=100, verbose_name=u"联系电话")
    postcode = models.CharField(max_length=6, verbose_name=u"邮政编码", blank=True)
    is_default = models.BooleanField(default=False, verbose_name=u"是否为默认")

class UserSource(models.Model):
    """
        user baidu source keyword
    """
    user = models.ForeignKey(User)
    keyword = models.CharField(max_length=50, verbose_name=u"收件人姓名", blank=False, null=False, default="")


#发给所有人
def send_public_message(sender, instance, **kwargs):
    if instance.mtype == "public":
        from wanglibao_account import message
        message.send_all.apply_async(kwargs={
            "msgTxt_id": instance.id
        })

post_save.connect(send_public_message, sender=MessageText)
