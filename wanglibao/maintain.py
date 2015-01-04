# coding=utf-8
from decimal import Decimal, ROUND_DOWN
from django.forms import model_to_dict
from marketing.models import Reward, RewardRecord, IntroducedBy
from order.models import Order
from order.utils import OrderHelper
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_p2p.models import P2PRecord, Earning
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User
from wanglibao_account import message as inside_message
from wanglibao_sms.tasks import send_messages
from wanglibao.templatetags.formatters import safe_phone_str


def send_award():
    # start = timezone.datetime(2014, 11, 1, 0, 00, 00)
    # end = timezone.datetime(2014, 12, 31, 23, 59, 59)
    start = timezone.datetime(2015, 1, 1, 0, 00, 00)
    end = timezone.datetime(2015, 1, 5, 23, 59, 59)

    p2p_records = P2PRecord.objects.filter(create_time__range=(start, end), catalog='申购').values("user").annotate(
        dsum=Sum('amount'))

    ban_nian_xunlei = 0
    yi_nian_xunlei = 0
    huafei = 0
    huafei_count = 0
    jd_500 = 0
    jd_1000 = 0
    ipad_mini = 0
    ipad_air = 0
    iphone_6 = 0
    iphone_6_plus = 0

    for record in p2p_records:
        if 1000 <= record["dsum"] < 50000:
            reward_user_ban_nian_xunlei(record["user"], u"半年迅雷会员", record["dsum"])
            ban_nian_xunlei += 1
            print u"发放半年迅雷会员第%s个" % ban_nian_xunlei
        if record["dsum"] >= 50000:
            reward_user_yi_nian_xunlei(record["user"], u"一年迅雷会员", record["dsum"])
            yi_nian_xunlei += 1
            print u"发放一年迅雷会员第%s个" % yi_nian_xunlei
        if 10000 <= record["dsum"] < 100000:
            huafei_50 = int(int(record["dsum"]) / 10000) * 50
            reward_user_hua_fei(record["user"], u"理财送话费", record["dsum"], huafei_50)
            print u"发放话费%s元" % huafei_50
            huafei += huafei_50
            huafei_count += 1
        if 100000 <= record["dsum"] < 200000:
            reward_user_jd_500(record["user"], u"500元京东卡", record["dsum"])
            jd_500 += 1
            print u"发放500元京东卡第%s个" % jd_500
        if 200000 <= record["dsum"] < 400000:
            reward_user_jd_1000(record["user"], u"1000元京东卡", record["dsum"])
            jd_1000 += 1
            print u"发放1000元京东卡第%s个" % jd_1000
        if 400000 <= record["dsum"] < 500000:
            reward_user_apple(record["user"], u"满就送ipad mini",record["dsum"], "iPad mini 3(16G WLAN)")
            ipad_mini += 1
            print u"发放ipad mini 第%s个" % ipad_mini
        if 500000 <= record["dsum"] < 1000000:
            reward_user_apple(record["user"], u"满就送ipad air",record["dsum"], "iPad Air 2(16G WLAN)")
            ipad_air += 1
            print u"发放ipad air 第%s个" % ipad_air
        if 1000000 <= record["dsum"] < 1200000:
            reward_user_apple(record["user"], u"满就送iphone6",record["dsum"], u"iPhone 6 (16G 4.7英寸)")
            iphone_6 += 1
            print u"发放iphone6第%s个" % iphone_6
        if record["dsum"] >= 1200000:
            reward_user_apple(record["user"], u"满就送iphone6 plus",record["dsum"], u"iPhone 6 Plus(16G 5.5英寸)")
            iphone_6_plus += 1
            print u"发放iphone6 plus第%s个" % iphone_6_plus

    new_user = IntroducedBy.objects.filter(bought_at__range=(start, end)).exclude(
        introduced_by__username__startswith="channel").exclude(introduced_by__wanglibaouserprofile__utype__gt=0)
    amount_05 = 0
    for first_user in new_user:
        first_record = P2PRecord.objects.filter(user=first_user.user, create_time__range=(start, end),
                                                catalog='申购').earliest("create_time")
        if first_record.amount >= 1000:
            amount_05_one = Decimal(Decimal(first_record.amount) * Decimal(0.005) * (
            Decimal(first_record.product.period) / Decimal(12))).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            reward_user_5(first_user.user, first_user.introduced_by, u"邀请送收益", amount_05_one, first_record.product)
            if first_user.introduced_by is not None and first_user.introduced_by.wanglibaouserprofile is not None and first_user.introduced_by is not None and first_user.introduced_by.wanglibaouserprofile is not None:
                print u"%s邀请了%s，活动期间首笔交易%s元，%s获得%s元奖金" % (
                first_user.introduced_by.wanglibaouserprofile.name, first_user.user.wanglibaouserprofile.name,
                first_record.amount, first_user.introduced_by.wanglibaouserprofile.name, amount_05_one)
            amount_05 += amount_05_one

    print "*********************************"
    print "*********************************"
    print "*************Done****************"
    print "*********************************"
    print "*********************************"
    print u"发放半年迅雷会员%s个" % ban_nian_xunlei
    print u"发放一年迅雷会员第%s个" % yi_nian_xunlei
    print u"发放话费%s元" % huafei
    print u"发放人数%s" % huafei_count
    print u"发放500元京东卡%s个" % jd_500
    print u"发放1000元京东卡%s个" % jd_1000
    print u"发放ipad mini %s个" % ipad_mini
    print u"发放ipad air %s个" % ipad_air
    print u"发放iphone6%s个" % iphone_6
    print u"发放iphone6 plus%s个" % iphone_6_plus
    print u"发放邀请送千5活动，送出%s元" % amount_05
    print "*********************************"
    print "*********************************"
    print "*************Done****************"
    print "*********************************"
    print "*********************************"


def reward_user(user_id, reward_type, is_used, content, title):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    if is_used is True:
        reward.is_used = True
        reward.save()
    RewardRecord.objects.create(user=user, reward=reward, description=content)
    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": title,
        "content": content,
        "mtype": "activity"
    })

    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [content]
    })


def reward_user_ban_nian_xunlei(user_id, reward_type, amount):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    reward.is_used = True
    reward.save()

    message_content = u"亲爱的%s您好：<br/> 您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得半年迅雷白金会员奖励。<br/>\
                      激活码：%s，有效期至2015年12月31日。<br/>\
                      <a href = 'http://pay.vip.xunlei.com/baijin.html'>立即兑换</a><br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (user.wanglibaouserprofile.name, amount, reward.content)

    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": u"满额送活动",
        "content": message_content,
        "mtype": "activity"
    })
    text_content = u"【网利宝】您在“满额就送”活动期间，获得半年迅雷白金会员奖励。激活码：%s，有效期至2015年12月31日。回复TD退订4008-588-066【网利宝】" % reward.content
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })
    RewardRecord.objects.create(user=user, reward=reward, description=message_content)


def reward_user_yi_nian_xunlei(user_id, reward_type, amount):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    reward.is_used = True
    reward.save()

    message_content = u"亲爱的%s您好：<br/> 您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得一年迅雷白金会员奖励。<br/>\
                      激活码：%s，有效期至2015年12月31日。<br/>\
                      <a href = 'http://pay.vip.xunlei.com/baijin.html'>立即兑换</a><br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (user.wanglibaouserprofile.name, amount, reward.content)

    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": u"满额送活动",
        "content": message_content,
        "mtype": "activity"
    })
    text_content = u"【网利宝】您在“满额就送”活动期间，获得一年迅雷白金会员奖励。激活码：%s，有效期至2015年12月31日。回复TD退订4008-588-066【网利宝】" % reward.content
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })
    RewardRecord.objects.create(user=user, reward=reward, description=message_content)


def reward_user_hua_fei(user_id, reward_type, amount, huafei):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()

    message_content = u"亲爱的%s您好：<br/> 您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得%s元话费奖励。<br/>\
                      3个工作日内充值至您的注册手机号码，请注意查收！<br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (user.wanglibaouserprofile.name, amount, huafei)

    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": u"满额送活动",
        "content": message_content,
        "mtype": "activity"
    })
    text_content = u"【网利宝】您在“满额就送”活动期间，获得s%元话费奖励。话费将于3个工作日内充值至您的注册手机号码，请注意查收！回复TD退订4008-588-066【网利宝】" % huafei
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })
    RewardRecord.objects.create(user=user, reward=reward, description=message_content)


def reward_user_jd_500(user_id, reward_type, amount):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    reward.is_used = True
    reward.save()

    message_content = u"亲爱的%s您好：<br/> 您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得500元京东礼品卡。<br/>\
                      京东卡密为：%s，有效期至2015年12月31日。<br/>\
                      <a href = 'http://www.jd.com'>立即使用</a><br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (user.wanglibaouserprofile.name, amount, reward.content)

    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": u"满额送活动",
        "content": message_content,
        "mtype": "activity"
    })
    text_content = u"【网利宝】您在“满额就送”活动期间，获得500元京东礼品卡。京东卡密为：%s，有效期至2015年12月31日。回复TD退订4008-588-066【网利宝】" % reward.content
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })
    RewardRecord.objects.create(user=user, reward=reward, description=message_content)


def reward_user_jd_1000(user_id, reward_type, amount):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    reward.is_used = True
    reward.save()

    message_content = u"亲爱的%s您好：<br/> 您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得1000元京东礼品卡。<br/>\
                      京东卡密为：%s，有效期至2015年12月31日。<br/>\
                      <a href = 'http://www.jd.com'>立即使用</a><br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (user.wanglibaouserprofile.name, amount, reward.content)

    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": u"满额送活动",
        "content": message_content,
        "mtype": "activity"
    })
    text_content = u"【网利宝】您在“满额就送”活动期间，获得1000元京东礼品卡。京东卡密为：%s，有效期至2015年12月31日。回复TD退订4008-588-066【网利宝】" % reward.content
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })
    RewardRecord.objects.create(user=user, reward=reward, description=message_content)


def reward_user_apple(user_id, reward_type, amount, apple):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()

    message_content = u"亲爱的%s您好：<br/> 您在“满额就送”活动期间，累计投资%s元，根据活动规则，您获得%s。<br/>\
                      奖品将于7个工作日内为您寄出，请注意查收。<br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (user.wanglibaouserprofile.name, amount, apple)

    inside_message.send_one.apply_async(kwargs={
        "user_id": user_id,
        "title": u"满额送活动",
        "content": message_content,
        "mtype": "activity"
    })
    text_content = u"【网利宝】您在“满额就送”活动期间，获得%s。奖品将于7个工作日内为您寄出，请注意查收。回复TD退订4008-588-066【网利宝】" % apple
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })
    RewardRecord.objects.create(user=user, reward=reward, description=message_content)


def reward_user_5(user, introduced_by, reward_type, got_amount, product):
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()

    text_content = u"【网利宝】您在邀请好友送收益的活动中，获得%s元收益，收益已经发放至您的网利宝账户。请注意查收。回复TD退订4008-588-066【网利宝】" % got_amount
    send_messages.apply_async(kwargs={
        "phones": [user.wanglibaouserprofile.phone],
        "messages": [text_content]
    })

    earning = Earning()
    earning.amount = got_amount
    earning.type = 'I'
    earning.product = product
    order = OrderHelper.place_order(introduced_by, Order.ACTIVITY, u"邀请送收益活动赠送",
                                    earning=model_to_dict(earning))
    earning.order = order
    keeper = MarginKeeper(introduced_by, order.pk)

    # 赠送活动描述
    desc = u'%s,邀请好友首次理财活动中，活赠%s元' % (introduced_by.wanglibaouserprofile.name, got_amount)
    earning.margin_record = keeper.deposit(got_amount, description=desc)
    earning.user = introduced_by
    earning.save()

    message_content = u"亲爱的%s您好：<br/> 您在邀请好友送收益的活动中，您的好友%s在活动期间完成首次投资，根据活动规则，您获得%s元收益。<br/>\
                      <a href = 'https://www.wanglibao.com/accounts/home/'>查看账户余额</a><br/>\
                      感谢您对我们的支持与关注。<br/>\
                      网利宝" % (
    introduced_by.wanglibaouserprofile.name, safe_phone_str(user.wanglibaouserprofile.phone), got_amount)
    RewardRecord.objects.create(user=introduced_by, reward=reward, description=message_content)

    inside_message.send_one.apply_async(kwargs={
        "user_id": introduced_by.id,
        "title": u"邀请送收益活动",
        "content": message_content,
        "mtype": "activity"
    })