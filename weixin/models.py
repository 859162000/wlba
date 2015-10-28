# encoding:utf-8
from __future__ import unicode_literals
from collections import OrderedDict
import datetime

from django.db import models
from django.contrib.auth.models import User

from .common.wechat import gen_token
from wechatpy.client import WeChatClient
from wechatpy.client.api.qrcode import WeChatQRCode


class Account(models.Model):
    """
    微信公众号
    """
    ACCOUNT_CLASSIFY = (
        ('0', '未认证订阅号'),
        ('1', '微信认证订阅号'),
        ('2', '未认证服务号'),
        ('3', '微信认证服务号'),
        ('4', '微信公众平台测试号'),
    )

    name = models.CharField('公众号名称', max_length=120, null=False)
    classify = models.CharField('公众号类型', max_length=10, choices=ACCOUNT_CLASSIFY)
    token = models.CharField('公众号token', max_length=32, default=gen_token)
    original_id = models.CharField('公众号原始ID', max_length=32, blank=True, db_index=True)
    app_id = models.CharField('app id', max_length=32)
    app_secret = models.CharField('app secret', max_length=64)
    access_token_content = models.CharField('access token', max_length=512, blank=True)
    access_token_expires_at = models.DateTimeField('access token过期时间', auto_now_add=True, blank=True)
    jsapi_ticket_content = models.CharField('jsapi ticket', max_length=512, blank=True)
    jsapi_ticket_expires_at = models.DateTimeField('jsapi ticket过期时间', auto_now_add=True, blank=True)
    oauth_access_token_content = models.CharField('oauth access token', max_length=512, blank=True)
    oauth_access_token_expires_at = models.DateTimeField('oauth access token过期时间', auto_now_add=True, blank=True, null=True)
    oauth_refresh_token = models.CharField('oauth refresh token', max_length=512, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name_plural = '微信公众号'
        ordering = ['-created_at']

    @staticmethod
    def _now():
        from django.utils.timezone import utc
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        return now

    def update_access_token(self):
        now = self._now()
        client = WeChatClient(self.app_id, self.app_secret)
        res = client.fetch_access_token()
        self.access_token_content = res.get('access_token')
        self.access_token_expires_at = now + datetime.timedelta(seconds=res.get('expires_in') - 60)
        self.save()

    @property
    def access_token(self):
        now = self._now()

        if now > self.access_token_expires_at:
            self.update_access_token()

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

    @property
    def oauth_access_token(self):
        now = self._now()
        if now > self.oauth_access_token_expires_at:
            # 超时刷新
            pass
        return self.oauth_access_token_content

    @oauth_access_token.setter
    def oauth_access_token(self, access_token):
        self.oauth_access_token_content = access_token

    @property
    def oauth_access_token_expires_in(self):
        raise AttributeError('not read field')

    @oauth_access_token_expires_in.setter
    def oauth_access_token_expires_in(self, expires):
        now = self._now()
        self.oauth_access_token_expires_at = now + datetime.timedelta(seconds=expires - 60)

    @property
    def weixin_original_id(self):
        raise AttributeError('not read filed')

    @weixin_original_id.setter
    def weixin_original_id(self, value):
        if not self.original_id or self.original_id != value:
            self.original_id = value
            self.save()

    def get_user_info(self, openid=None, lang='zh_CN'):
        """Get user infomation
        :param openid: WeChat openid, optional
        :param access_token: WeChat OAuth2 access token, optional
        :param lang: Preferred language code, optional
        :return: JSON data
        """
        access_token = self.access_token
        client = WeChatClient(self.app_id, self.app_secret)
        return client._get(
            'user/info',
            params={
                'access_token': access_token,
                'openid': openid,
                'lang': lang
            }
        )

    def empty_data(self):
        now = self._now()
        self.access_token_content = ''
        self.access_token_expires_at = now
        self.jsapi_ticket_content = ''
        self.jsapi_ticket_expires_at = now
        self.oauth_access_token_content = ''
        self.oauth_access_token_expires_at = now
        self.oauth_refresh_token = ''
        self.save()

class QrCode(models.Model):
    account_original_id = models.CharField('所属公众号原始ID', max_length=32, blank=True, db_index=True)
    ticket = models.CharField('ticket', max_length=512, null=False)
    expire_at = models.DateTimeField('ticket过期时间', auto_now_add=True, blank=True, null=True)
    url = models.CharField('url', max_length=512, null=False)
    qrcode_url = models.CharField('qrcode_url', max_length=512, null=False)
    scene_str = models.CharField('scene_str', max_length=128, null=False)
    create_at = models.DateTimeField('生成时间', auto_now_add=True, blank=True, null=True)
    def ticket_generate(self):
        return u'<a href="/weixin/api/generate/ticket/?id=%s" target="_self">生成ticket</a>' % (self.id,)
    ticket_generate.short_description = u'生成ticket'
    ticket_generate.allow_tags = True
    def qrcode_link(self):
        return u'<a href="%s" target="_blank">查看二维码</a>' % (WeChatQRCode.get_url(self.ticket))
    qrcode_link.short_description = u'查看二维码'
    qrcode_link.allow_tags = True
    class Meta:
        verbose_name_plural = '微信二维码'
        ordering = ['-account_original_id', '-create_at']

# 公众号类型
class WeixinAccounts(object):
    data = OrderedDict()
    account_main = {
        'id': 'gh_f758af6347b6',
        'name': '网利宝',
        'app_id': 'wx896485cecdb4111d',
        'app_secret': 'b1e152144e4a4974cd06b8716faa98e1',
        'classify': '微信认证服务号',
        'mch_id': '1237430102',
        'key': 'mmeBOdBjuovQOgPPSp1qZFONbHS9pkZn',
        'token': '6d0dbaca',
        'qrcode_url': '/static/imgs/admin/qrcode_for_gh_f758af6347b6_258.jpg'
    }
    account_sub_1 = {
        'id': 'gh_77c09ff2f3a3',
        'name': '网利宝',
        'app_id': 'wx110c1d06158c860b',
        'app_secret': '2523d084edca65b6633dae215967a23f',
        'classify': '微信认证订阅号',
        'EncodingAESKey': '3QXabFsqXV64Bvdc4EvRciOfvWbYw7Fud38J8ianHmx',
        'token': '695bc700',
        'qrcode_url': '/static/imgs/admin/qrcode_for_gh_77c09ff2f3a3_258.jpg'
    }
    account_test = {
        'id': 'gh_d852bc2cead2',
        'name': '测试号',
        'app_id': 'wx22c7a048569d3e7e',
        'app_secret': '1340e746fb4c3719d405fdc27752bc6f',
        'classify': '微信公众平台测试号',
        'token': '6ad01528',
        'qrcode_url': '/static/imgs/admin/qrcode_for_gh_d852bc2cead2_258.jpg'
    }

    id = None
    name = None
    app_id = None
    app_secret = None
    classify = None
    mch_id = None
    key = None
    EncodingAESKey = None
    token = None

    client_cache = None
    db_account_cache = None
    host_url = None

    def __init__(self, account_key=None):
        self.append_account()
        if account_key:
            data = self.data.get(account_key)
            self.account_key = account_key
            for key, value in data.items():
                setattr(self, key, value)

    @classmethod
    def append_account(cls):
        cls.data['main'] = cls.account_main
        cls.data['sub_1'] = cls.account_sub_1
        cls.data['test'] = cls.account_test

    @classmethod
    def account_classify(cls):
        return dict(map(lambda item: (item[1], item[0]), dict(Account.ACCOUNT_CLASSIFY).items()))

    @classmethod
    def syncdb(cls):
        instance = cls()
        account_classify = cls.account_classify()
        for k, v in instance.data.items():
            account, created = Account.objects.get_or_create(original_id=v.get('id'))
            account_data = [account.name, account.classify, account.token, account.app_id, account.app_secret]
            dict_data = [v.get('name'), account_classify.get(v.get('classify')), v.get('token'), v.get('app_id'), v.get('app_secret')]
            if ''.join(account_data) != ''.join(dict_data):
                account.name = v.get('name')
                account.classify = account_classify.get(v.get('classify'))
                account.token = v.get('token')
                account.app_id = v.get('app_id')
                account.app_secret = v.get('app_secret')
                account.save()
                account.empty_data()

    @classmethod
    def get(cls, key):
        return cls(key)

    @classmethod
    def all(cls):
        _all = []
        cls.append_account()
        for account_key, _ in cls.data.items():
            _all.append(cls(account_key))
        return _all

    @property
    def db_account(self):
        if not self.db_account_cache:
            account, created = Account.objects.get_or_create(original_id=self.id)
            self.db_account_cache = account
        return self.db_account_cache

    @property
    def weixin_client(self):
        if not self.client_cache:
            self.client_cache = WeChatClient(self.app_id, self.app_secret, self.access_token)
        return self.client_cache

    @property
    def access_token(self):
        return self.db_account.access_token

    @property
    def jsapi_ticket(self):
        return self.db_account.jsapi_ticket

    @property
    def connect_url(self):
        from django.core.urlresolvers import reverse
        return '{}{}'.format(self.host_url, reverse('weixin_join', kwargs={'account_key': self.account_key}))

    @property
    def material_count_cache_time(self):
        # 公众号素材总数缓存时间 单位：秒
        # 测试号 1000次／天 缓存300秒
        # 公众号 5000次／天 缓存20秒
        account_classify = self.account_classify()
        if account_classify.get(self.classify) == 4:
            return 300
        return 20


class AuthorizeInfo(models.Model):
    access_token = models.CharField('access token', max_length=512)
    access_token_expires_at = models.DateTimeField('access token过期时间', auto_now_add=True, blank=True)
    refresh_token = models.CharField('refresh token', max_length=512, blank=True)


    def check_access_token(self):
        now = Account._now()
        if now > self.access_token_expires_at:
            return False
        return True



class WeixinUser(models.Model):
    SEX_DATA = (
        (1, '男'),
        (2, '女'),
        (0, '未知')
    )

    subscribe = models.IntegerField('是否订阅该公众号标识', default=0)
    openid = models.CharField('用户标识', max_length=128, db_index=True)
    nickname = models.CharField('用户昵称', max_length=64, blank=True)
    sex = models.IntegerField('用户性别', choices=SEX_DATA, default=0)
    city = models.CharField('用户所在城市', max_length=128, blank=True)
    country = models.CharField('用户所在国家', max_length=128, blank=True)
    province = models.CharField('用户所在省份', max_length=128, blank=True)
    language = models.CharField('用户的语言', max_length=64, blank=True)
    headimgurl = models.URLField('用户头像', blank=True)
    subscribe_time = models.IntegerField('用户关注时间', default=0)
    account_original_id = models.CharField('所属公众号原始ID', max_length=32, blank=True, db_index=True)
    user = models.ForeignKey(User, null=True)
    unionid = models.CharField('用户唯一标识', max_length=128, blank=True)
    scene_id = models.CharField('渠道', max_length=64, blank=True, null=True)
    auth_info = models.ForeignKey(AuthorizeInfo, null=True)




class Material(models.Model):
    voice_count = models.IntegerField('音频总数', default=0)
    video_count = models.IntegerField('视频总数', default=0)
    image_count = models.IntegerField('图片总数', default=0)
    news_count = models.IntegerField('图文总数', default=0)
    expires_at = models.DateTimeField('缓存过期时间', auto_now_add=True)
    account = models.OneToOneField(Account)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    @staticmethod
    def _now():
        from django.utils.timezone import utc
        now = datetime.datetime.utcnow().replace(tzinfo=utc)
        return now

    def is_expires_in(self):
        now = self._now()
        return now < self.expires_at

    def data(self):
        return {
            'voice_count': self.voice_count,
            'video_count': self.video_count,
            'image_count': self.image_count,
            'news_count': self.news_count
        }

    def update_data(self, data, expires_in=60):
        now = self._now()
        self.voice_count = data.get('voice_count')
        self.video_count = data.get('video_count')
        self.image_count = data.get('image_count')
        self.news_count = data.get('news_count')
        self.expires_at = now + datetime.timedelta(seconds=expires_in)
        self.save()


class MaterialImage(models.Model):
    file = models.ImageField('图片', upload_to='material_image', null=True)
    name = models.CharField('素材名称', max_length=128)
    media_id = models.CharField('素材ID', max_length=64, db_index=True)
    update_time = models.IntegerField('上传时间')
    account = models.ForeignKey(Account)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)


class MaterialNews(models.Model):
    content = models.TextField('图文消息内容')
    media_id = models.CharField('素材ID', max_length=64)
    update_time = models.IntegerField('上传时间')
    account = models.ForeignKey(Account)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)


class ReplyContent(models.Model):
    MEDIA_CLASSIFY = (
        ('text', '文本'),
        ('image', '图片'),
        ('news', '图文'),
        # ('voice', '音频'),
        # ('video', '视频'),
    )

    classify = models.CharField('回复类型', choices=MEDIA_CLASSIFY, max_length=10, default=MEDIA_CLASSIFY[0][0])
    media_id = models.CharField('媒体ID', max_length=64)
    content = models.CharField('内容', max_length=300)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    def resource(self):
        data = {'type': self.classify}
        if self.classify == 'text':
            data['data'] = self.content
        if self.classify == 'news':
            import json
            res = MaterialNews.objects.get(media_id=self.media_id)
            data['data'] = json.loads(res.data)
        data['data'] = self.media_id
        return data


class ReplyRule(models.Model):
    """
    关键字匹配
    """
    PATTERN_CHOICES = (
        (0, '回复全部'),
        (1, '回复第一个'),
        (2, '随机回复一个'),
    )

    name = models.CharField('规则名称', max_length=64)
    replies = models.ManyToManyField(ReplyContent)
    pattern = models.IntegerField('回复规则', choices=PATTERN_CHOICES, default=PATTERN_CHOICES[0][0])
    account = models.ForeignKey(Account)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)


class ReplyKeyword(models.Model):

    PATTERN_CHOICES = (
        (0, '未全匹配'),
        (1, '已全匹配'),
    )

    content = models.CharField('关键字内容', max_length=30)
    pattern = models.IntegerField('匹配模式', choices=PATTERN_CHOICES)
    rule_reply = models.ForeignKey(ReplyRule)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

