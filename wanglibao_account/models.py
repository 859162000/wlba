# encoding: utf8
from django.contrib.auth import get_user_model
from django.db import models


class IdVerification(models.Model):
    """
    This is a table stores all id verification info. The verify method should
    check this table first
    """

    id_number = models.CharField(u"身份证号", max_length=128, db_index=True)
    name = models.CharField(u"姓名", max_length=32)
    is_valid = models.BooleanField(u"验证结果", default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class VerifyCounter(models.Model):
    """
    The table stores the count each user called the id verify api
    """

    user = models.OneToOneField(get_user_model())
    count = models.IntegerField(u'尝试认证次数', default=0)

    def __unicode__(self):
        return u'%s: %d' % (self.user.wanglibaouserprofile.phone, self.count)
