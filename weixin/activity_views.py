# encoding:utf-8
from django.views.generic import TemplateView
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
import logging
import base64
import datetime
from wanglibao_account.backends import invite_earning
from weixin.models import UserDailyActionRecord, SeriesActionActivity
from experience_gold.models import ExperienceEventRecord



logger = logging.getLogger("weixin")
# https://open.weixin.qq.com/connect/oauth2/authorize?appid=wx18689c393281241e&redirect_uri=http://2ea0ef54.ngrok.io/weixin/award_index/&response_type=code&scope=snsapi_base&state=1#wechat_redirect

class InviteWeixinFriendTemplate(TemplateView):
    template_name = "sub_invite_server.jade"

    def get_context_data(self, **kwargs):
        user = self.request.user
        earning = 0
        if user:
            earning = invite_earning(user)

        return {
            "earning":earning,
            "callback_host":settings.CALLBACK_HOST,
            "url": base64.b64encode(user.wanglibaouserprofile.phone),
        }
    def dispatch(self, request, *args, **kwargs):
        self.url_name = 'sub_invite'
        return super(InviteWeixinFriendTemplate, self).dispatch(request, *args, **kwargs)

class GetSignShareInfo(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = request.user
        today = datetime.date.today()
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).date()
        sign_record = UserDailyActionRecord.objects.filter(user=user, create_date=today, action_type=u'sign_in').first()
        share_record = UserDailyActionRecord.objects.filter(user=user, create_date=today, action_type=u'share').first()
        data = {}
        sign_info = data.setdefault('sign_in', {})
        sign_total_count = UserDailyActionRecord.objects.filter(user=user, action_type=u'sign_in').count()
        sign_info['sign_total_count'] = sign_total_count
        sign_info['status'] = False
        if sign_record and sign_record.status:
            sign_info['status'] = True
            sign_info['amount']=0
            sign_info['continue_days'] = sign_record.continue_days
            if sign_record.experience_record_id:
                experience_record = ExperienceEventRecord.objects.get(id=sign_record.experience_record_id)
                sign_info['amount']=experience_record.event.amount
        else:
            yesterday_sign_record = UserDailyActionRecord.objects.filter(user=user, create_date=yesterday, action_type=u'sign_in').first()
            sign_info['continue_days'] = 0
            if yesterday_sign_record:
                sign_info['continue_days'] = yesterday_sign_record.continue_days
        nextDayNote = None
        activities = SeriesActionActivity.objects.filter(is_stopped=False, start_at__lte=timezone.now(), end_at__gte=timezone.now()).all()
        length = len(activities)
        if length > 0:
            maxDayNote=activities[length-1].days
            recycle_continue_days = sign_info['continue_days'] % (maxDayNote + 1)
            for activity in activities:
                if activity.days >= recycle_continue_days:
                    nextDayNote=activity.days
                    break
            # needDays = nextDayNote-recycle_continue_days
            sign_info['nextDayNote'] = nextDayNote
            # sign_info['needDays'] = needDays
            sign_info['current_day'] = recycle_continue_days

        share_info = data.setdefault('share', {})
        share_info['status'] = False
        if share_record and share_record.status:
            share_info['status'] = True
            share_info['amount']=0
            if share_record.experience_record_id:
                experience_record = ExperienceEventRecord.objects.get(id=share_record.experience_record_id)
                share_info['amount']=experience_record.event.amount

        return Response({"ret_code": 0, "data": data})










