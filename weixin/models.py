# encoding:utf-8
from django.db import models
from django.db.models.signals import pre_save
from .common.wechat import gen_token
from wechatpy.client import WeChatClient
import datetime


class Account(models.Model):
    """
    微信公众号
    """
    ACCOUNT_CLASSIFY = (
        ('0', u'未认证订阅号'),
        ('1', u'微信认证订阅号'),
        ('2', u'未认证服务号'),
        ('3', u'微信认证服务号'),
    )

    name = models.CharField(u'公众号名称', max_length=120, null=False)
    classify = models.CharField(u'公众号类型', max_length=10, choices=ACCOUNT_CLASSIFY)
    token = models.CharField(u'公众号token', max_length=32, default=gen_token)
    app_id = models.CharField(u'app id', max_length=32)
    app_secret = models.CharField(u'app secret', max_length=64)
    access_token_content = models.CharField(u'access token', max_length=512)
    access_token_expires_at = models.DateTimeField(u'access token过期时间', auto_now_add=True)
    jsapi_ticket_content = models.CharField(u'jsapi ticket', max_length=512)
    jsapi_ticket_expires_at = models.DateTimeField(u'jsapi ticket过期时间', auto_now_add=True)
    created_at = models.DateTimeField(u'创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = u'微信公众号'
        ordering = ['-created_at']

    @staticmethod
    def _now():
        from django.utils.timezone import utc
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        return now

    @property
    def access_token(self):
        now = self._now()
        if now > self.access_token_expires_at:
            client = WeChatClient(self.app_id, self.app_secret)
            res = client.fetch_access_token()
            self.access_token_content = res.get('access_token')
            self.access_token_expires_at = now + datetime.timedelta(seconds=res.get('expires_in') - 60)
            self.save()

        return self.access_token_content

    @property
    def jsapi_ticket(self):
        now = self._now()

        if now > self.jsapi_ticket_expires_at:
            client = WeChatClient(self.app_id, self.app_secret, self.access_token)
            res = client.jsapi.get_ticket()
            self.jsapi_ticket_content = res.get('ticket')
            self.jsapi_ticket_expires_at = now + datetime.timedelta(seconds=res.get('expires_in') - 60)
            self.save()

        return self.jsapi_ticket_content

#
# class Reply(models.Model):
#     MEDIA_CLASSIFY = (
#         ('text', u'文本'),
#         ('image', u'图片'),
#         ('voice', u'音频'),
#         ('video', u'视频'),
#         ('news', u'图文'),
#     )
#
#     classify = models.CharField(u'回复类型', choices=MEDIA_CLASSIFY, max_length=10)
#     media_id = models.CharField(u'媒体ID', max_length=64)
#     content = models.CharField(u'内容', max_length=10000)
#
#     def resource(self):
#         data = {'type': self.classify}
#         if self.classify == 'text':
#             data['data'] = self.content
#         if self.classify == 'news':
#             import json
#             res = News.objects.get(media_id=self.media_id)
#             data['data'] = json.loads(res.data)
#         data['data'] = self.media_id
#         return data
#
#
# class RuleReply(models.Model):
#     """
#     关键字匹配
#     """
#     name = models.CharField(u'规则名称', max_length=64)
#     replies = models.ManyToManyField(Reply)
#     pattern = models.CharField(u'回复', max_length=10)
#     created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
#
#
# class Keyword(models.Model):
#
#     MATCH_PATTERN = (
#         ('0', u'未全匹配'),
#         ('1', u'已全匹配'),
#     )
#
#     content = models.CharField(u'关键字内容', max_length=30)
#     pattern = models.CharField(u'匹配模式', max_length=2, choices=MATCH_PATTERN)
#     rule_reply = models.ForeignKey(RuleReply)
#     created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
#
#
# class News(models.Model):
#     """
#     图文素材
#     """
#     media_id = models.CharField(u'素材ID', max_length=64)
#     data = models.CharField(u'图文内容', max_length=10000)
#     created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
#
#


# class Image(models.Model):
#     """
#     图片素材
#     """
#     media_id = models.CharField(u'素材ID')
#     created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
#
#
# class Voice(models.Model):
#     """
#     音频素材
#     """
#     media_id = models.CharField(u'素材ID')
#     created_at = models.DateTimeField(u'创建时间', auto_now_add=True)
#
#
# class Video(models.Model):
#     """
#     音频素材
#     """
#     media_id = models.CharField(u'素材ID')
#     created_at = models.DateTimeField(u'创建时间', auto_now_add=True)

