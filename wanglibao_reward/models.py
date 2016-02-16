# encoding: utf-8
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from wanglibao_activity.models import Activity
from wanglibao_redpack.models import RedPackEvent
from experience_gold.models import ExperienceEvent
from marketing.models import Reward
class WanglibaoActivityGiftGlobalCfg(models.Model):
    """
        活动发奖全局配置
    """
    TYPE = (
        (0, u'all'),
        (1, u'pc'),
        (2, u'weixin'),
        (3, u'app'),
    )
    activity = models.ForeignKey(Activity, default=None)
    chances = models.IntegerField(default=3, verbose_name=u'共有几次抽奖机会')
    when_register = models.DateTimeField(default=timezone.now, null=False, verbose_name=u"什么时候注册的用户可以参与活动")
    terminal_type = models.IntegerField(choices=TYPE, default=0, verbose_name=u'活动终端')
    amount = models.IntegerField(default=0, verbose_name=u'抽奖投资门槛')

    class Meta:
        verbose_name = u'活动奖品全局配置'
        verbose_name_plural = u'活动奖品全局配置'


class WanglibaoActivityGift(models.Model):
    """ 活动奖品配置表 """
    TYPE = (
        (0, u'红包'),
        (1, u'加息券'),
        (2, u'百分比红包'),
        (3, u'体验金'),
    )
    gift_id = models.IntegerField(default=0, verbose_name=u'奖品编号')
    activity = models.ForeignKey(Activity, default=None)
    redpack = models.ForeignKey(RedPackEvent, default=None)
    cfg = models.ForeignKey(WanglibaoActivityGiftGlobalCfg, default=None)
    type = models.IntegerField(choices=TYPE, default=0, verbose_name=u'奖品类型')
    chances = models.IntegerField(default=3, verbose_name=u'配置用户有几次抽奖机会')
    name = models.CharField(max_length=128, default=u'红包', verbose_name=u'奖品名称', help_text=u'例如：红包、加息券、优惠券等')
    rate = models.CharField(max_length=128, verbose_name=u'获奖概率', help_text=u"获奖概率请直接填写数字，例如：获奖概率为20%，填写 20,也支持填写区间值 20~30")
    send_rate = models.IntegerField(default=0, verbose_name=u'发奖速度', help_text=u"发奖速度请直接填写数字,每天发多少个, 0表示每天不限量")
    total_count = models.IntegerField(default=0, verbose_name=u'奖品总个数', help_text=u'如果为0，表示不限个数')
    each_day_count = models.IntegerField(default=0, verbose_name=u'每天奖品个数', help_text=u'如果为0，表示不限个数')
    channels = models.CharField(max_length=128, verbose_name=u'奖品发放渠道', help_text=u'各个渠道之间用空格分开; 如果为空，表示全渠道')
    valid = models.BooleanField(default=True, verbose_name=u'该奖项是否启动', help_text=u'奖项默认是启用的')

    class Meta:
        verbose_name = u'活动奖品配置'
        verbose_name_plural = u'活动奖品配置'


class WanglibaoUserGift(models.Model):
    """
        用户获奖记录
    """
    TYPE = (
        (0, u'红包'),
        (1, u'加息券'),
        (2, u'优惠券'),
        (3, u'体验金'),
    )
    SEND = (
        (0, u'YES'),
        (1, u'NO'),
        (2, u'INVALID')
    )
    activity = models.ForeignKey(Activity)
    user = models.ForeignKey(User, default=None, null=True)
    rules = models.ForeignKey(WanglibaoActivityGift, default=None)
    identity = models.CharField(max_length=64, verbose_name=u'用户标号', help_text=u'例如手机号')
    index = models.IntegerField(default=0, verbose_name=u'特定活动内的奖品编号')
    type = models.IntegerField(choices=TYPE, default=0, verbose_name=u'奖品类型')
    name = models.CharField(max_length=128, default=u'红包', verbose_name=u'奖品名称', help_text=u'例如：红包、加息券、优惠券等')
    valid = models.IntegerField(default=1, choices=SEND, verbose_name=u'奖品是否已发')
    amount = models.FloatField(default=0, verbose_name=u'奖品额度')
    get_time = models.DateTimeField(auto_now_add=True, verbose_name=u'用户领奖的时间')
    # add by hb on 2015-12-14
    redpack_record_id = models.IntegerField(default=0, verbose_name=u'优惠券发放流水ID')

    class Meta:
        verbose_name = u'用户活动获奖记录'
        verbose_name_plural = u'用户活动获奖记录'

class WanglibaoActivityGiftOrder(models.Model):
    valid_amount = models.IntegerField(default=0, verbose_name=u'此次分享剩余的抽奖机会')
    order_id = models.IntegerField(default=0, unique=True, verbose_name=u'订单号')

    class Meta:
        verbose_name = u'订单分享表'
        verbose_name_plural = u'订单分享表'

class WanglibaoWeixinRelative(models.Model):
    """
        手机号-网利宝用户-微信openid关系表
    """
    user = models.ForeignKey(User, default=None, blank=True, null=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=32, default="", verbose_name=u'电话号码')
    nick_name = models.CharField(max_length=128, default=u'', verbose_name=u'微信昵称')
    openid = models.CharField(max_length=128, default=u'', verbose_name=u'')
    img = models.CharField(max_length=255, default=u'', verbose_name=u'微信头像')
    phone_for_fencai = models.CharField(max_length=32, default="", verbose_name=u'电话号码')

    class Meta:
        verbose_name = u'微信网利宝关系表'
        verbose_name_plural = u'微信网利宝关系表'

class WanglibaoActivityReward(models.Model):
    order_id =models.IntegerField(default=0, verbose_name=u'订单ID')
    user = models.ForeignKey(User, related_name='reward_owner', default=None, blank=True, null=True, on_delete=models.SET_NULL)
    redpack_event = models.ForeignKey(RedPackEvent, default=None, blank=True, null=True, verbose_name=u'用户获得的红包')
    reward = models.ForeignKey(Reward, default=None, blank=True, null=True, verbose_name=u'用户获得的奖品')
    experience = models.ForeignKey(ExperienceEvent, default=None, blank=True, null=True, verbose_name=u'用户获得的体验金')
    activity = models.CharField(default='', max_length=256, verbose_name=u'活动名称')
    qrcode = models.ImageField(upload_to='qrcode', null=True, blank=True, verbose_name=u'获奖请求二维码')
    when_dist = models.IntegerField(default=0, verbose_name=u'什么时候发奖')
    left_times = models.IntegerField(default=0, verbose_name=u'还剩几次抽奖机会')
    join_times = models.IntegerField(default=0, verbose_name=u'用户参与抽奖的次数')
    channel = models.CharField(default='', null=False, max_length=64, verbose_name=u'来自哪个渠道')
    has_sent = models.BooleanField(default=False, null=False, verbose_name=u'奖品已经发送')
    p2p_amount = models.IntegerField(default=0, null=False, verbose_name=u'购买的标量')
    create_at = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_at = models.DateTimeField(auto_now_add=True, verbose_name=u'更新时间')

    class Meta:
        verbose_name = u'发奖记录表'
        verbose_name_plural = u'发奖记录表'

class WeixinAnnualBonus(models.Model):
    openid = models.CharField(u'微信用户标识', max_length=128, unique=True)
    nickname = models.CharField(u'用户昵称', max_length=64, null=True)
    headimgurl = models.URLField(u'用户头像', null=True)
    phone = models.CharField(u'手机号码', max_length=64, unique=True)
    user = models.ForeignKey(User, default=None, null=True, db_index=True)
    #user_id = models.IntegerField(default=None, null=True, db_index=True)
    is_new = models.BooleanField(u'是否新用户', default=False)
    is_max = models.BooleanField(u'年终奖是否已封顶', default=False)
    is_pay = models.BooleanField(u'是否已领取', default=False)
    min_annual_bonus = models.IntegerField(u'Min年终奖', default=1000)
    max_annual_bonus = models.IntegerField(u'Max年终奖', default=1000)
    annual_bonus = models.IntegerField(u'年终奖', default=1000)
    good_vote = models.IntegerField(u'好评数', default=0)
    bad_vote = models.IntegerField(u'差评数', default=0)
    create_time = models.DateTimeField(u'创建时间', null=True)
    share_count = models.IntegerField(u'分享数', default=0)
    visit_time = models.DateTimeField(u'最近分享时间', null=True)
    visit_count = models.IntegerField(u'访问数', default=0)
    visit_time = models.DateTimeField(u'最近访问时间', null=True)
    update_time = models.DateTimeField(u'最近评价时间', null=True)
    pay_time = models.DateTimeField(u'领取时间', null=True)

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

    def toJSON_filter(self, filters=None):
        fields = []
        if filters:
            for field in filters:
                fields.append(field)
        else:
            for field in self._meta.fields:
                fields.append(field.name)

        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)

        #import json
        #return json.dumps(d)
        return d

class WeixinAnnulBonusVote(models.Model):
    to_openid = models.CharField(u'受评微信用户标识', max_length=128, null=False, db_index=True)
    from_openid = models.CharField(u'评价微信用户标识', max_length=128, null=False, db_index=True)
    from_nickname = models.CharField(u'评价微信用户昵称', max_length=64, null=True)
    from_headimgurl = models.URLField(u'评价微信用户头像', null=True)
    from_ipaddr = models.CharField(u'评价来源IP地址', max_length=128, null=True)
    is_good_vote = models.BooleanField(u'是否好评', default=True)
    current_good_vote = models.IntegerField(u'当前好评数', default=0)
    current_bad_vote = models.IntegerField(u'当前差评数', default=0)
    current_annual_bonus = models.IntegerField(u'当前年终奖', default=1000)
    create_time = models.DateTimeField(u'评价时间', null=True)

    class Meta:
        unique_together = (("from_openid", "to_openid"),)  # 联合唯一索引

    def toJSON(self):
        import json
        return json.dumps(dict([(attr, getattr(self, attr)) for attr in [f.name for f in self._meta.fields]]))

    def toJSON_filter(self, filters=None):
        fields = []
        if filters:
            for field in filters:
                fields.append(field)
        else:
            for field in self._meta.fields:
                fields.append(field.name)

        d = {}
        for attr in fields:
            d[attr] = getattr(self, attr)

        import json
        return json.dumps(d)

class ActivityRewardRecord(models.Model):
    user = models.ForeignKey(User, db_index=True)
    create_date = models.DateField(u'创建日期', auto_now_add=True,  db_index=True)
    activity_code = models.CharField(u'活动代码*', max_length=64, null=True)
    activity_code_time = models.DateTimeField(u'领取activity_code对应奖品时间', null=True)
    redpack_record_ids = models.CharField(u'活动代码对应的领取优惠券流水ｉｄ', max_length=64, null=True)
    experience_record_ids = models.CharField(u'活动代码对应的领取体验金流水ｉｄ', max_length=64, null=True)
    redpack_record_id = models.IntegerField(default=0, verbose_name=u'优惠券发放流水ID', null=True)
    redpack_record_id_time = models.DateTimeField(u'领取redpack_rule对应奖品时间', null=True)


    class Meta:
        unique_together = (("user", "create_date"),)  # 联合唯一索引

