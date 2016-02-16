#!/usr/bin/env python
# encoding: utf8

#from django.contrib.auth import get_user_model
import time
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from marketing.models import Channels, ChannelsNew
from file_storage.storages import AliOSSStorageForCover


class IdVerification(models.Model):
    """
    This is a table stores all id verification info. The verify method should
    check this table first
    """

    id_number = models.CharField(u"身份证号", max_length=128, db_index=True)
    name = models.CharField(u"姓名", max_length=32)
    id_photo = models.ImageField(upload_to='id_photos', blank=True, null=True,
                                 verbose_name=u'身份证头像')
    is_valid = models.BooleanField(u"验证结果", default=False)
    description = models.CharField(u"验证结果描述", max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    update_verify = models.BooleanField(u"更新", default=False)

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


class UserThreeOrder(models.Model):
    user = models.ForeignKey(User)
    order_on = models.ForeignKey(Channels, verbose_name=u'订单渠道')
    request_no = models.CharField(unique=True, max_length=30, verbose_name=u'请求流水号')
    result_code = models.CharField(max_length=30, blank=True, verbose_name=u'受理结果编码')
    msg = models.CharField(max_length=255, blank=True, verbose_name=u'受理结果消息')
    created_at = models.DateTimeField(u'下单时间', auto_now_add=True)
    answer_at = models.DateTimeField(u'订单反馈时间', blank=True, null=True)

    class Meta:
        verbose_name_plural = u'渠道订单记录'


class Binding(models.Model):
    """
        third app bind table, store bind related
    """
    user = models.ForeignKey(User)
    btype = models.CharField(max_length=20, verbose_name=u"类型")
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
    detect_callback = models.BooleanField(u"回调检测", default=False)

    class Meta:
        verbose_name_plural = u'用户绑定'

message_type = (
    ("withdraw", u"提现通知"),
    ("pay", u"充值通知"),
    ("amortize", u"项目还款"),
    ("activityintro", u"活动介绍"),
    ("activity", u"活动奖励"),
    ("bids", u"流标通知"),
    ("purchase", u"投标通知"),
    ("fullbid", u"满标"), #给管理员发
    ("loaned", u"投标成功"),#给持仓人发
    #("audited", "满标已审核"),
    ("public", u"发给所有"),
    ("invite", u"邀请奖励"),
    ("coupon", u"加息奖励")
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
    ACTION = (
        ('default', u'浏览'),
        ('register', u'注册'),
        ('login', u'登录'),
        ('verified', u'实名'),
        ('binding', u'绑卡'),
        ('pay', u'充值'),
        ('buy', u'投资'),
        ('withdraw', u'提现')
    )
    user = models.ForeignKey(User)
    keyword = models.CharField(max_length=50, verbose_name=u"收件人姓名", blank=False, null=False,  default='')
    website = models.CharField(max_length=256, verbose_name=u'网站地址', blank=False, null=False,  default='')
    site_name = models.CharField(max_length=64, verbose_name=u'站点名称', blank=True, null=False, default='')
    action = models.CharField(max_length=128, verbose_name=u'此次访问的最终行为', choices=ACTION, null=False, default='default')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=u"入库时间", default='2015-01-01 00:00:00')

    class Meta:
        verbose_name_plural = u'关键词统计'
        verbose_name = u'关键词统计'

class UserPhoneBook(models.Model):
    user = models.ForeignKey(User)
    phone = models.CharField(max_length=64, blank=True, help_text=u'通讯录电话', db_index=True)
    name = models.CharField(max_length=50, blank=True, verbose_name=u"姓名")
    is_register = models.BooleanField(default=False, verbose_name=u"是否注册")
    is_invite = models.BooleanField(default=False, verbose_name=u"是否邀请")
    invite_at = models.DateTimeField(null=True, blank=True, verbose_name=u'最后一次邀请提醒时间', db_index=True)
    alert_at = models.DateTimeField(null=True, blank=True, verbose_name=u'最后一次投资提醒时间')
    created_at = models.DateTimeField(auto_now_add=True, default=timezone.now())
    is_used = models.BooleanField(default=True, verbose_name=u"是否使用", help_text=u'默认使用')


class ManualModifyPhoneRecord(models.Model):

    STATUS_CHOICES = (
        (u"待初审",   u"待初审"),
        (u"初审待定", u"初审待定"),
        (u"初审驳回", u"初审驳回"),
        (u"待复审",   u"待复审"),
        (u"复审通过", u"复审通过"),
        (u"复审驳回", u"复审驳回"),
    )
    # 待初审　初审待定　初审驳回　待复审　复审通过 复审驳回
    user = models.ForeignKey(User)
    phone = models.CharField(max_length=64, blank=True, help_text=u'手机号码')
    id_front_image = models.ImageField(upload_to='modify_phone/id_card', storage=AliOSSStorageForCover(), blank=True, verbose_name=u'身份证正面照片', help_text=u'身份证正面照片')
    id_back_image = models.ImageField(upload_to='modify_phone/id_card', storage=AliOSSStorageForCover(), blank=True, verbose_name=u'身份证反面照片', help_text=u'身份证反面照片')
    id_user_image = models.ImageField(upload_to='modify_phone/id_card', storage=AliOSSStorageForCover(), blank=True, verbose_name=u'手持身份证照片', help_text=u'手持身份证照片')
    new_phone = models.CharField(max_length=64, blank=True, help_text=u'新的手机号码')
    status = models.CharField(max_length=16, default=u'初审中', db_index=True,
                              choices=STATUS_CHOICES,
                              verbose_name=u'申请状态')
    remarks = models.CharField(max_length=64, blank=True, help_text=u'客服在审核过程中的备注')
    created_at = models.DateTimeField(u'提交申请时间', auto_now_add=True)
    update_at = models.DateTimeField(u'申请更新时间', auto_now=True)
    class Meta:
        verbose_name_plural = u'人工修改手机号'
        ordering = ('-created_at',)

class SMSModifyPhoneRecord(models.Model):
    STATUS_CHOICES = (
        (u"短信修改手机号提交", u"短信修改手机号提交"),
        (u"短信修改手机号成功", u"短信修改手机号成功"),
    )
    user = models.ForeignKey(User)
    phone = models.CharField(max_length=64, blank=True, help_text=u'手机号码')
    new_phone = models.CharField(max_length=64, blank=True, help_text=u'新的手机号码')
    status = models.CharField(max_length=16, default=u'短信修改手机号提交', db_index=True,
                              choices=STATUS_CHOICES,
                              verbose_name=u'短信修改状态')

    created_at = models.DateTimeField(u'提交申请时间', auto_now_add=True)
    update_at = models.DateTimeField(u'申请更新时间', auto_now=True)
    class Meta:
        verbose_name_plural = u'短信修改手机号'
        ordering = ('-created_at',)


#发给所有人
def send_public_message(sender, instance, **kwargs):
    if instance.mtype == "public":
        from wanglibao_account import message
        message.send_all.apply_async(kwargs={
            "msgTxt_id": instance.id
        })

post_save.connect(send_public_message, sender=MessageText)
