from marketing.models import Reward, RewardRecord
from wanglibao_p2p.models import P2PRecord
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.models import User
from wanglibao_account import message as inside_message
from wanglibao_sms.tasks import send_messages

def send_award():

    start = timezone.datetime(2014, 11, 1,0,00,00)
    end = timezone.datetime(2014,12,31,23,59,59)

    p2p_records = P2PRecord.objects.filter(create_time__range=(start, end), catalog='申购').values("user").annotate(dsum=Sum('amount'))


    ban_nian_xunlei = 0
    yi_nian_xunlei = 0
    huafei = 0
    jd_500 = 0
    jd_1000 = 0
    ipad_mini = 0
    ipad_air = 0
    iphone_6 = 0
    iphone_6_plus = 0

    for record in p2p_records:
        if 1000 <= record["dsum"] < 50000:
            reward_user_ban_nian_xunlei(record["user"],u"半年迅雷会员",record["dsum"])
            ban_nian_xunlei += 1
            print u"发放半年迅雷会员第%s个" % ban_nian_xunlei
        if record["dsum"] >= 50000:
            reward_user_yi_nian_xunlei(record["user"],u"一年迅雷会员",record["dsum"])
            yi_nian_xunlei += 1
            print u"发放一年迅雷会员第%s个" % yi_nian_xunlei
        if 10000 <= record["dsum"] < 100000:
            reward_user_hua_fei(record["user"],u"理财送话费",record["dsum"],huafei_50)
            huafei_50 = record["dsum"] / 10000
            print u"发放话费%s元" % huafei_50 * 50
            huafei += huafei_50 * 50
        if 100000 <= record["dsum"] < 200000:
            reward_user_jd_500(record["user"],u"500元京东卡",record["dsum"])
            jd_500 += 1
            print u"发放500元京东卡第%s个" % jd_500
        if 200000 <= record["dsum"] < 400000:
            reward_user_jd_1000(record["user"],u"1000元京东卡",record["dsum"])
            jd_1000 += 1
            print u"发放1000元京东卡第%s个" % jd_1000
        if 400000 <= record["dsum"] < 500000:
            reward_user_apple(record["user"],u"满就送ipad mini","iPad mini 3(16G WLAN)")
            ipad_mini += 1
            print u"发放ipad mini 第%s个" % ipad_mini
        if 500000 <= record["dsum"] < 1000000:
            reward_user_apple(record["user"],u"满就送ipad air","iPad Air 2(16G WLAN)")
            ipad_air += 1
            print u"发放ipad air 第%s个" % ipad_air
        if 1000000 <= record["dsum"] < 1200000:
            reward_user_apple(record["user"],u"满就送iphone",u"iPhone 6 (16G 4.7英寸)")
            iphone_6 += 1
            print u"发放iphone6第%s个" % iphone_6
        if record["dsum"] > 1200000:
            reward_user_apple(record["user"],u"满就送iphone",u"iPhone 6 Plus(16G 5.5英寸)")
            iphone_6_plus += 1
            print u"发放iphone6 plus第%s个" % iphone_6_plus
    print "*********************************"
    print "*********************************"
    print "*************Done****************"
    print "*********************************"
    print "*********************************"
    print u"发放半年迅雷会员%s个" % ban_nian_xunlei
    print u"发放一年迅雷会员第%s个" % yi_nian_xunlei
    print u"发放话费%s元" % huafei
    print u"发放500元京东卡%s个" % jd_500
    print u"发放1000元京东卡%s个" % jd_1000
    print u"发放ipad mini %s个" % ipad_mini
    print u"发放ipad air %s个" % ipad_air
    print u"发放iphone6%s个" % iphone_6
    print u"发放iphone6 plus%s个" % iphone_6_plus
    print "*********************************"
    print "*********************************"
    print "*************Done****************"
    print "*********************************"
    print "*********************************"

def reward_user(user_id,reward_type,is_used,content,title):
    user = User.objects.get(pk=user_id)
    reward = Reward.objects.filter(is_used=False, type=reward_type).first()
    if is_used is True:
        reward.is_used = True
        reward.save()
    RewardRecord.objects.create(user=user, reward=reward,description=content)
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


def reward_user_ban_nian_xunlei(user_id,reward_type,amount):
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
    RewardRecord.objects.create(user=user, reward=reward,description=message_content)


def reward_user_yi_nian_xunlei(user_id,reward_type,amount):
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
    RewardRecord.objects.create(user=user, reward=reward,description=message_content)

def reward_user_hua_fei(user_id,reward_type,amount,huafei):
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
    RewardRecord.objects.create(user=user, reward=reward,description=message_content)

def reward_user_jd_500(user_id,reward_type,amount):
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
    RewardRecord.objects.create(user=user, reward=reward,description=message_content)


def reward_user_jd_1000(user_id,reward_type,amount):
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
    RewardRecord.objects.create(user=user, reward=reward,description=message_content)


def reward_user_apple(user_id,reward_type,amount,apple):
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
    RewardRecord.objects.create(user=user, reward=reward,description=message_content)