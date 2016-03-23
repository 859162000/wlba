# -*- coding: utf-8 -*-
from wanglibao.celery import app
from utils import sendWechatPhoneRewardByRegister, getTodayTop10Ranks, getYesterdayTop10Ranks
from wanglibao_account.auth_backends import User
from wanglibao_redis.backend import redis_backend
from misc.models import Misc
from wanglibao_reward.models import ActivityRewardRecord
import json
import datetime
from django.db import transaction
import logging
from django.utils import timezone
from wanglibao_redpack.models import RedPackEvent
from wanglibao_redpack.backends import give_activity_redpack_new
from wanglibao_activity.models import Activity
from marketing.utils import local_to_utc

logger = logging.getLogger('wanglibao_reward')

@app.task
def sendWechatPhoneReward(user_id):
    try:
        user = User.objects.get(id=user_id)
        sendWechatPhoneRewardByRegister(user)
    except:
        pass

# @app.task
def updateRedisTopRank():
    try:
        top_ranks = getTodayTop10Ranks()
        redis_backend()._lpush('top_ranks', top_ranks)
    except Exception,e:
        logger.error("====updateRedisTopRank======="+e.message)


@app.task
def sendYesterdayTopRankAward():
    rank_activity = Activity.objects.filter(code='march_awards').first()
    # utc_now = timezone.now()
    # today_start = local_to_utc(datetime.datetime.now(), 'min')
    yesterday = datetime.datetime.now()-datetime.timedelta(1)
    yesterday_end = datetime.datetime(year=yesterday.year, month=yesterday.month, day=yesterday.day, hour=23, minute=59, second=59)
    yesterday_end = local_to_utc(yesterday_end, "")
    # yesterday_start = local_to_utc(yesterday, 'min')
    if rank_activity and ((not rank_activity.is_stopped) or (rank_activity.is_stopped and rank_activity.stopped_at>yesterday_end)) and rank_activity.start_at<=yesterday_end and rank_activity.end_at>=yesterday_end:
        top_ranks = getYesterdayTop10Ranks()
        misc = Misc.objects.filter(key='march_awards').first()
        march_awards = json.loads(misc.value)
        rank_awards = march_awards['rank_awards']
        uids = [rank['user'] for rank in top_ranks]
        users = User.objects.filter(id__in=uids).all()
        now_date = datetime.date.today()
        for index, rank in enumerate(top_ranks):
            redpack_event_id = rank_awards[index]
            redpack_event = RedPackEvent.objects.filter(id=int(redpack_event_id)).first()
            if not redpack_event:
                logger.error('排名奖励，第%s名的奖励配置的id为%s的红包不存在,导致该排名的用户%s没有得到'%(index+1, redpack_event_id, rank['user']))
                continue
            for user in users:
                if user.id == rank['user']:
                    if not ActivityRewardRecord.objects.filter(create_date=now_date, activity_code=u'march_awards', user=user).exists():
                        ActivityRewardRecord.objects.create(
                        user=user,
                        activity_code=u'march_awards',
                        activity_desc=u'获得%s排名%s奖励'%(yesterday.date(), (index+1))
                        )
                    with transaction.atomic():
                        rank_reward_record = ActivityRewardRecord.objects.select_for_update().filter(create_date=now_date, activity_code=u'march_awards', user=user).first()
                        if not rank_reward_record.redpack_record_id:
                            status, messege, redpack_record_id = give_activity_redpack_new(user, redpack_event, 'all')
                            if not status:
                                logger.error('排名奖励，排名第%s名的用户%s没有得到%s,因为%s'%(index+1,rank['user'], redpack_event_id, messege))
                                break
                            rank_reward_record.redpack_record_id = redpack_record_id
                            rank_reward_record.redpack_record_id_time = timezone.now()
                            rank_reward_record.status = True
                            rank_reward_record.save()
                    break


