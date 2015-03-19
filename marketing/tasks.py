# coding=utf-8
from celery.utils.log import get_task_logger
from datetime import datetime
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from marketing.models import TimelySiteData, PlayList
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