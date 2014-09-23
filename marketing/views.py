from datetime import date, timedelta, datetime
from collections import defaultdict

from django.views.generic import  TemplateView
from django.db.models import Count
from wanglibao_profile.models import WanglibaoUserProfile
from django.contrib.auth.models import User
from wanglibao_buy.models import TradeHistory


# Create your views here.

class MarketingView(TemplateView):

    template_name = 'diary.jade'

    def get_context_data(self, **kwargs):

        d0 = date(2014, 7, 01)
        d1 = date.today()

        users = User.objects.filter(date_joined__range=(d0, d1)).extra({'each_day': 'date(date_joined)'}).values('each_day').annotate(joined_num=Count('id'))
        trades = TradeHistory.objects.filter(business_type='022', create_date__range=(d0, d1), user__date_joined=(date_joined)).extra({'each_day': 'date(create_date)'}).values('each_day').annotate(trade_num=Count('id'))

        days = [d0 + timedelta(days=x) for x in range((d1-d0).days + 1)]

        d = defaultdict(dict)

        for l in (users, trades):
            for elem in l:
                d[elem['each_day']].update(elem)

        result = d.values()


        return {
            'all': result,
            'trades': trades,
            'days': days
        }