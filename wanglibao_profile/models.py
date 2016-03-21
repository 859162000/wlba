# encoding: utf-8

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from wanglibao_p2p.models import P2PRecord


class WanglibaoUserProfile(models.Model):
    # user = models.OneToOneField(get_user_model(), primary_key=True)
    user = models.OneToOneField(User, primary_key=True)

    nick_name = models.CharField(max_length=32, blank=True, help_text=u'昵称')

    phone = models.CharField(max_length=64, blank=True, help_text=u'手机号码')
    phone_verified = models.BooleanField(default=False, help_text=u'手机号码是否已验证')

    id_is_valid = models.BooleanField(help_text=u'身份证是否通过验证', default=False)
    id_valid_time = models.DateTimeField(blank=True, null=True, verbose_name=u"实名认证时间")

    utype = models.CharField(u'用户类型', max_length=10, default='0')

    is_bind_card = models.BooleanField(u'是否完成首次绑卡', default=False)
    first_bind_time = models.DateTimeField(u"首次绑卡时间", blank=True, null=True)

    def __unicode__(self):
        return "phone: %s nickname: %s  %s" % (self.phone, self.nick_name, self.user.username)


def create_profile(sender, **kw):
    """
    Create the user profile when a user object is created
    """
    user = kw["instance"]
    if kw["created"]:
        profile = WanglibaoUserProfile(user=user)
        profile.save()

# post_save.connect(create_profile, sender=get_user_model(), dispatch_uid="users-profile-creation-signal")
post_save.connect(create_profile, sender=User, dispatch_uid="users-profile-creation-signal")
