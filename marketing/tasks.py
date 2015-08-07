# coding=utf-8
from celery.utils.log import get_task_logger
from datetime import datetime
from django.contrib.auth.models import User
from django.db import transaction, connection
from django.db.models import Sum
from django.utils import timezone
from marketing.models import TimelySiteData, PlayList, IntroducedByReward, Reward
from marketing.utils import local_to_utc
from wanglibao_account import message as inside_message
from wanglibao.celery import app
from wanglibao_margin.models import Margin
from wanglibao_redpack.backends import give_activity_redpack
from wanglibao_redpack.models import RedPackEvent
from wanglibao_p2p.models import AmortizationRecord, P2PRecord
from misc.views import MiscRecommendProduction


logger = get_task_logger(__name__)


@app.task
def generate_pc_index_data():
    # 累计交易金额
    p2p_amount = P2PRecord.objects.filter(catalog='申购').aggregate(Sum('amount'))['amount__sum']
    # 累计交易人数
    user_number = P2PRecord.objects.filter(catalog='申购').values('id').count()

    # 提前还款的收益
    income_pre = AmortizationRecord.objects.filter(catalog='提前还款').aggregate(Sum('interest'))['interest__sum']
    income_pre = income_pre if income_pre else 0
    # 非提前还款的收益（已发收益＋未发收益）
    sql = "select sum(a.interest) from wanglibao_p2p_useramortization as a left join wanglibao_p2p_productamortization as b on a.product_amortization_id=b.id LEFT JOIN (select distinct product_id from wanglibao_p2p_p2pequity where confirm=True and not exists (select distinct a.product_id from wanglibao_p2p_productamortization a, wanglibao_p2p_amortizationrecord b where a.id=b.amortization_id and b.catalog='提前还款') ) as c on b.product_id=c.product_id;"
    cursor = connection.cursor()
    cursor.execute(sql)
    income = cursor.fetchone()
    cursor.close()
    user_income = income[0] + income_pre
    key = 'pc_index_data'

    m = MiscRecommendProduction(key=MiscRecommendProduction.KEY_PC_DATA, desc=MiscRecommendProduction.DESC_PC_DATA)
    data = {
        'p2p_amount': float(p2p_amount),
        'user_number': user_number,
        'user_income': float(user_income)
    }
    m.update_value(value={key: data})


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
        # text_content = u"【网利宝】您在邀请好友送收益的活动中，获得%s元收益，收益已经发放至您的网利宝账户。请注意查收。" % got_amount
        # send_messages.apply_async(kwargs={
        #     "phones": [introduced_by.wanglibaouserprofile.phone],
        #     "messages": [text_content]
        # })

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
        earning.margin_record = keeper.deposit(got_amount, description=desc, catalog=u"邀请首次赠送")
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
            reward.first_bought_at = record.create_time
            reward.first_amount = record.amount

            # 计算被邀请人首笔投资总收益（收益年化）
            reward.first_reward = get_base_decimal(Decimal(record.amount) * Decimal(record.product.expected_earning_rate) * Decimal(0.01) * Decimal(record.product.period) / 12)

            # 邀请人活取被邀请人首笔投资（投资年化）
            got_amount = get_base_decimal(Decimal(record.amount) * Decimal(percent) * Decimal(0.01) * Decimal(record.product.period) / 12)
            reward.introduced_reward = got_amount

            reward.activity_start_at = start_utc
            reward.activity_end_at = end_utc
            reward.activity_amount_min = Decimal(amount_min)
            reward.percent_reward = Decimal(percent)
            reward.checked_status = 0
            # 新增字段
            if first_user.user.wanglibaouserprofile.utype == '0':
                reward.user_send_amount = got_amount
            if first_user.introduced_by.wanglibaouserprofile.utype == '0':
                reward.introduced_send_amount = got_amount

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
    # A 邀请 B
    # A 邀请人， B 被邀请人
    for record in records:
        # 为被邀请人发收益
        if record.user.wanglibaouserprofile.utype == '0':
            reward_earning(record, record.user, record.introduced_reward, record.product, flag=1)
            phone_user.append(record.user.wanglibaouserprofile.phone)

        # 为邀请人发收益
        if record.introduced_by_person.wanglibaouserprofile.utype == '0':
            reward_earning(record, record.introduced_by_person, record.introduced_reward, record.product, flag=2)
            phone_user.append(record.introduced_by_person.wanglibaouserprofile.phone)

        if record.user.wanglibaouserprofile.utype != '0' and record.introduced_by_person.wanglibaouserprofile.utype != '0':
            IntroducedByReward.objects.filter(id=record.id).update(checked_status=1, checked_at=timezone.now())

    phone_user = list(set(phone_user))
    if phone_user:
        # 发送短信
        # text_content = u'好友邀请收益已经到账，请在个人账户中进行查看。'
        # send_messages.apply_async(kwargs={
        #     "phones": phone_user,
        #     "messages": [text_content]
        # })

        # 发放站内信
        inside_message.send_batch.apply_async(kwargs={
            "users": phone_user,
            "title": u"邀请送收益活动",
            "content": u'好友邀请收益已经到账，请在个人账户中进行查看。',
            "mtype": "activity"
        })


def reward_earning(record, reward_user, got_amount, product, flag):
    from wanglibao_p2p.models import Earning
    from order.utils import OrderHelper
    from order.models import Order
    from django.forms import model_to_dict
    from wanglibao_margin.marginkeeper import MarginKeeper

    # 发放收益
    earning = Earning()
    earning.amount = got_amount
    earning.type = 'I'
    earning.product = product
    order = OrderHelper.place_order(
        reward_user,
        Order.ACTIVITY,
        u"邀请送收益活动赠送",
        earning=model_to_dict(earning))
    earning.order = order
    keeper = MarginKeeper(reward_user, order.pk)

    # 赠送活动描述
    desc = u'%s,邀请好友理财活动中，获赠%s元' % (reward_user.wanglibaouserprofile.name, got_amount)
    earning.margin_record = keeper.deposit(got_amount, description=desc, catalog=u"邀请赠送")
    earning.user = reward_user
    earning.save()

    if flag == 1:
        IntroducedByReward.objects.filter(id=record.id).update(checked_status=1, checked_at=timezone.now(), user_send_status=True)
    else:
        IntroducedByReward.objects.filter(id=record.id).update(checked_status=1, checked_at=timezone.now(), introduced_send_status=True)
