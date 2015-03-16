# coding=utf-8
from celery.utils.log import get_task_logger
from django.db.models import Sum
from marketing.models import TimelySiteData
from wanglibao.celery import app
from wanglibao_margin.models import Margin

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
def send_redpack():
    from django.contrib.auth.models import User
    from django.db import transaction
    from django.utils import timezone
    from marketing.models import PlayList
    from wanglibao_redpack.models import RedPack, RedPackEvent, RedPackRecord
    from wanglibao_account import message as inside_message

    device_type = 'nil'
    now = timezone.now()

    play_list = PlayList.objects.filter(checked_status=1)

    for play in play_list:
        rps = RedPackEvent.objects.filter(
            give_mode=device_type,
            invalid=False,
            give_start_at__lte=now,
            give_end_at__gte=now,
            describe__startswith=play.redpackevent,
            amount=play.reward
        )

        with transaction.atomic():
            for x in rps:
                redpack = RedPack.objects.filter(event=x, status="unused").first()
                if redpack:
                    user = User.objects.get(id=play.user_id)
                    record = RedPackRecord()
                    record.user = user
                    record.redpack = redpack
                    record.change_platform = device_type
                    record.save()
                    # 更新数据库状态
                    PlayList.objects.filter(pk=play.id).update(checked_status=2)

                    # 发送站内信
                    message_content = u"您在每日投资打榜的活动中，投资{0}获得{1}元红包。<br/>\
                              感谢您对我们的支持与关注。<br/>\
                              网利宝".format(play.amount, play.reward)

                    inside_message.send_one.apply_async(kwargs={
                        "user_id": user.id,
                        "title": u"打榜送红包",
                        "content": message_content,
                        "mtype": "activity"
                    })
                    break