# coding=utf-8
from celery.utils.log import get_task_logger
from datetime import datetime
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from marketing.models import TimelySiteData, PlayList, IntroducedByReward, Reward
from marketing.utils import local_to_utc
from wanglibao_account import message as inside_message
from wanglibao.celery import app
from wanglibao_margin.models import Margin
from wanglibao_redpack.backends import give_activity_redpack
from wanglibao_redpack.models import RedPackEvent


logger = get_task_logger(__name__)

@app.task
def generate_site_data():
    result = Margin.objects.aggregate(p2p_margin=Sum('margin'), freeze_amount=Sum('freeze'))

    data = TimelySiteData()
    data.p2p_margin = result.get('p2p_margin', 0)
    data.freeze_amount = result.get('freeze_amount', 0)
    data.total_amount = data.p2p_margin + data.freeze_amount
    data.user_count = Margin.objects.all().count()

    data.save()


@app.task
def send_redpack(day, desc, rtype='nil'):
    now = timezone.now()
    day = datetime.strptime(day, '%Y-%m-%d')
    play_list = PlayList.objects.filter(
        checked_status=1,
        play_at=local_to_utc(day, 'min'),
        redpackevent=desc
    )

    for play in play_list:
        events = RedPackEvent.objects.filter(
            give_mode=rtype,
            invalid=False,
            give_start_at__lte=now,
            give_end_at__gte=now,
            describe=play.redpackevent,
            amount=play.reward
        )

        with transaction.atomic():
            for event in events:
                user = User.objects.get(id=play.user_id)
                status, msg = give_activity_redpack(user=user, event=event, device_type='pc')
                if status:
                    # 更新数据库状态
                    PlayList.objects.filter(pk=play.id).update(checked_status=2)

                    # 发送站内信
                    message_content = u"您在本次打榜活动中获奖，奖励红包已发送到您的账户，请在个人账户红包中查看。感谢您对我们的支持与关注。"

                    inside_message.send_one.apply_async(kwargs={
                        "user_id": user.id,
                        "title": u"打榜送红包",
                        "content": message_content,
                        "mtype": "activity"
                    })
                    break


@app.task
def add_introduced_award(start, end, amount_min, percent):
    from models import IntroducedBy
    from decimal import Decimal, ROUND_DOWN
    from wanglibao_p2p.models import P2PRecord

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    start_utc = local_to_utc(start, source_time='min')
    end_utc = local_to_utc(end, source_time='max')

    # 增加控制条件，没有被统计过才在统计生成
    if IntroducedByReward.objects.filter(activity_start_at=start_utc, activity_end_at=end_utc).exists():
        return False

    # print '============begin============', datetime.now()
    new_user = IntroducedBy.objects.filter(
        bought_at__range=(start_utc, end_utc)
    ).filter(
        introduced_by__isnull=False
    ).exclude(
        introduced_by__wanglibaouserprofile__utype__gt=0
    ).select_related('user')

    # print '============query new_user ok============', datetime.now()

    query_set_list = []
    num = 0
    for first_user in new_user:
        num += 1
        # everyone
        # print '============begin query p2precord============', datetime.now()
        first_record = P2PRecord.objects.filter(
            user=first_user.user,
            create_time__range=(start_utc, end_utc),
            catalog='申购',
            product__status__in=[
                u'满标待打款',
                u'满标已打款',
                u'满标待审核',
                u'满标已审核',
                u'还款中',
                u'已完成', ]
        ).order_by('create_time').first()

        # print '============end query p2precord============', datetime.now()

        # first trade min amount limit
        if first_record is not None and first_record.amount >= Decimal(amount_min):
            reward = IntroducedByReward()
            reward.user = first_user.user
            reward.introduced_by_person = first_user.introduced_by
            reward.product = first_record.product
            reward.first_bought_at = first_user.bought_at
            reward.first_amount = first_record.amount

            # 计算被邀请人首笔投资总收益
            amount_earning = Decimal(
                Decimal(first_record.amount) * (Decimal(first_record.product.period) / Decimal(12)) * Decimal(first_record.product.expected_earning_rate) * Decimal('0.01')
            ).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            reward.first_reward = amount_earning
            # 邀请人活取被邀请人首笔投资收益
            reward.introduced_reward = Decimal(
                Decimal(first_record.amount) * (Decimal(first_record.product.period) / Decimal(12)) * Decimal(percent) * Decimal('0.01')
            ).quantize(Decimal('0.01'), rounding=ROUND_DOWN)

            reward.activity_start_at = start_utc
            reward.activity_end_at = end_utc
            reward.activity_amount_min = Decimal(amount_min)
            reward.percent_reward = Decimal(percent)
            reward.checked_status = 0
            # reward.save()
            query_set_list.append(reward)

        # print '============one record end============', datetime.now()

        if len(query_set_list) == 100:
            IntroducedByReward.objects.bulk_create(query_set_list)
            query_set_list = []

    if len(query_set_list) > 0:
        IntroducedByReward.objects.bulk_create(query_set_list)


@app.task
def send_reward(start, end, amount_min, percent):
    from wanglibao_sms.tasks import send_messages
    from wanglibao_p2p.models import Earning
    from order.utils import OrderHelper
    from order.models import Order
    from django.forms import model_to_dict
    from wanglibao_margin.marginkeeper import MarginKeeper
    from wanglibao.templatetags.formatters import safe_phone_str
    from marketing.models import RewardRecord
    from decimal import Decimal

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    # 审核通过，给用户发放奖励
    reward_type = u'邀请送收益'
    records = IntroducedByReward.objects.filter(
        checked_status=0,
        activity_start_at=local_to_utc(start, source_time='min'),
        activity_end_at=local_to_utc(end, source_time='max'),
        activity_amount_min=Decimal(amount_min),
        percent_reward=Decimal(percent),
    )

    if not records.exists():
        return

    for record in records:
        # with transaction.atomic():
        user, introduced_by, reward_type, got_amount, product = record.user, record.introduced_by_person, reward_type, record.introduced_reward, record.product

        reward = Reward.objects.filter(is_used=False, type=reward_type).first()

        # 发送短信
        text_content = u"【网利宝】您在邀请好友送收益的活动中，获得%s元收益，收益已经发放至您的网利宝账户。请注意查收。回复TD退订4008-588-066【网利宝】" % got_amount
        send_messages.apply_async(kwargs={
            "phones": [introduced_by.wanglibaouserprofile.phone],
            "messages": [text_content]
        })

        # 发放收益
        earning = Earning()
        earning.amount = got_amount
        earning.type = 'I'
        earning.product = product
        order = OrderHelper.place_order(
            introduced_by,
            Order.ACTIVITY,
            u"邀请送收益活动赠送",
            earning=model_to_dict(earning))
        earning.order = order
        keeper = MarginKeeper(introduced_by, order.pk)

        # 赠送活动描述
        desc = u'%s,邀请好友首次理财活动中，活赠%s元' % (introduced_by.wanglibaouserprofile.name, got_amount)
        earning.margin_record = keeper.deposit(got_amount, description=desc)
        earning.user = introduced_by
        earning.save()

        # 发放站内信
        message_content = u"您在邀请好友送收益的活动中，您的好友%s在活动期间完成首次投资，根据活动规则，您获得%s元收益。<br/>\
                  <a href='/accounts/home/' target='_blank'>查看账户余额</a><br/>\
                  感谢您对我们的支持与关注。<br/>\
                  网利宝" % (safe_phone_str(user.wanglibaouserprofile.phone), got_amount)
        RewardRecord.objects.create(user=introduced_by, reward=reward, description=message_content)
        inside_message.send_one.apply_async(kwargs={
            "user_id": introduced_by.id,
            "title": u"邀请送收益活动",
            "content": message_content,
            "mtype": "activity"
        })

        IntroducedByReward.objects.filter(id=record.id).update(checked_status=1)


@app.task
def add_introduced_award_all(start, end, amount_min, percent):
    """ 邀请好友各的0.3%收益
    1、活动期间邀请注册账户？
    2、活动期间邀请注册账户购买产品
    3、邀请人是经纪人怎么处理？
    4、被邀请人是经纪人怎么处理？
    """

    from models import IntroducedBy
    from decimal import Decimal, ROUND_DOWN
    from wanglibao_p2p.models import P2PRecord

    from wanglibao_p2p.amortization_plan import get_base_decimal, get_final_decimal

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    start_utc = local_to_utc(start, source_time='min')
    end_utc = local_to_utc(end, source_time='max')

    # 增加控制条件，没有被统计过才在统计生成
    if IntroducedByReward.objects.filter(activity_start_at=start_utc, activity_end_at=end_utc).exists():
        return False

    new_user = IntroducedBy.objects.filter(
        bought_at__range=(start_utc, end_utc)
    ).filter(
        created_at__range=(start_utc, end_utc)
    ).filter(
        introduced_by__isnull=False
    ).select_related('user')

    if not new_user.exists():
        return

    query_set_list = []
    num = 0
    for first_user in new_user:
        num += 1

        # 所有投资的产品
        records = P2PRecord.objects.filter(
            user=first_user.user,
            create_time__range=(start_utc, end_utc),
            catalog='申购',
            product__status__in=[
                u'满标待打款',
                u'满标已打款',
                u'满标待审核',
                u'满标已审核',
                u'还款中',
                u'已完成', ]
        ).order_by('create_time')

        # 不存在投资记录，循环下一个用户
        if not records.exists():
            continue

        # 首笔投资大于200才有收益
        if records.first().amount < Decimal(amount_min):
            continue

        for record in records:
            reward = IntroducedByReward()
            reward.user = first_user.user
            reward.introduced_by_person = first_user.introduced_by
            reward.product = record.product
            reward.first_bought_at = first_user.bought_at
            reward.first_amount = record.amount

            # 计算被邀请人首笔投资总收益（收益年化）
            # reward.first_reward = get_base_decimal(record.amount * record.product.expected_earning_rate * 0.01 * record.product.period / 12)
            reward.first_reward = get_final_decimal(Decimal(record.amount) * Decimal(record.product.expected_earning_rate) * Decimal(0.01) * Decimal(record.product.period) / 12)

            # 邀请人活取被邀请人首笔投资（投资年化）
            # reward.introduced_reward = get_base_decimal(record.amount * percent * 0.01 * record.product.period / 12)
            reward.introduced_reward = get_final_decimal(Decimal(record.amount) * Decimal(percent) * Decimal(0.01) * Decimal(record.product.period) / 12)


            reward.activity_start_at = start_utc
            reward.activity_end_at = end_utc
            reward.activity_amount_min = Decimal(amount_min)
            reward.percent_reward = Decimal(percent)
            reward.checked_status = 0
            query_set_list.append(reward)

        if len(query_set_list) == 100:
            IntroducedByReward.objects.bulk_create(query_set_list)
            query_set_list = []

    if len(query_set_list) > 0:
        IntroducedByReward.objects.bulk_create(query_set_list)


@app.task
def send_reward_all(start, end, amount_min, percent):
    from decimal import Decimal
    from wanglibao_sms.tasks import send_messages

    start = datetime.strptime(start, '%Y-%m-%d')
    end = datetime.strptime(end, '%Y-%m-%d')

    # 审核通过，给用户发放奖励
    records = IntroducedByReward.objects.filter(
        checked_status=0,
        activity_start_at=local_to_utc(start, source_time='min'),
        activity_end_at=local_to_utc(end, source_time='max'),
        activity_amount_min=Decimal(amount_min),
        percent_reward=Decimal(percent),
    )

    if not records.exists():
        return

    phone_user = []
    for record in records:
        reward_earning(record, flag=1)
        reward_earning(record, flag=2)

        if record.introduced_by_person.wanglibaouserprofile.utype == '0':
            phone_user.append(record.introduced_by_person.wanglibaouserprofile.phone)
        if record.user.wanglibaouserprofile.utype == '0':
            phone_user.append(record.user.wanglibaouserprofile.phone)

    phone_user = list(set(phone_user))
    if phone_user:
        # 发送短信
        text_content = u'好友邀请收益已经到账，请在个人账户中进行查看。'
        send_messages.apply_async(kwargs={
            "phones": phone_user,
            "messages": [text_content]
        })

        # 发放站内信
        inside_message.send_batch.apply_async(kwargs={
            "users": phone_user,
            "title": u"邀请送收益活动",
            "content": u'好友邀请收益已经到账，请在个人账户中进行查看。',
            "mtype": "activity"
        })


def reward_earning(record, flag):
    from wanglibao_p2p.models import Earning
    from order.utils import OrderHelper
    from order.models import Order
    from django.forms import model_to_dict
    from wanglibao_margin.marginkeeper import MarginKeeper

    reward_type = u'邀请送收益'
    if flag == 1:
        user, introduced_by, reward_type, got_amount, product = record.user, record.introduced_by_person, reward_type, record.introduced_reward, record.product
    else:
        user, introduced_by, reward_type, got_amount, product = record.introduced_by_person, record.user, reward_type, record.introduced_reward, record.product

    # 只给普通用户发放收益
    if introduced_by.wanglibaouserprofile.utype != '0':
        return

    # 发放收益
    earning = Earning()
    earning.amount = got_amount
    earning.type = 'I'
    earning.product = product
    order = OrderHelper.place_order(
        introduced_by,
        Order.ACTIVITY,
        u"邀请送收益活动赠送",
        earning=model_to_dict(earning))
    earning.order = order
    keeper = MarginKeeper(introduced_by, order.pk)

    # 赠送活动描述
    desc = u'%s,邀请好友理财活动中，获赠%s元' % (introduced_by.wanglibaouserprofile.name, got_amount)
    earning.margin_record = keeper.deposit(got_amount, description=desc)
    earning.user = introduced_by
    earning.save()

    IntroducedByReward.objects.filter(id=record.id).update(checked_status=1)


