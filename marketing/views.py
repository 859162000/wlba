# encoding:utf-8

from datetime import date, timedelta, datetime
from collections import defaultdict

from django.views.generic import  TemplateView
from django.db.models import Count, F, Sum
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt

from wanglibao_profile.models import WanglibaoUserProfile
from django.contrib.auth.models import User
from wanglibao_buy.models import TradeHistory

from django.views.generic import TemplateView
from django.http.response import HttpResponse
from mock_generator import MockGenerator
from django.conf import settings



# Create your views here.

class MarketingView(TemplateView):

    template_name = 'diary.jade'

    def get_context_data(self, **kwargs):

        d0 = date(2014, 8, 01)
        d1 = date.today()

        users = User.objects.filter(date_joined__range=(d0, d1)).order_by('each_day')\
            .extra({'each_day': 'date(date_joined)'}).values('each_day')\
            .annotate(joined_num=Count('id'))


        trades = TradeHistory.objects.filter(business_type='022', create_date__range=(d0, d1)).order_by('each_day')\
            .extra({'each_day': 'date(create_date)'}).values('each_day')\
            .annotate(trade_num=Count('id'), amount=Sum('shares'))

        d = defaultdict(dict)

        for l in (users, trades):
            for elem in l:
                d[elem['each_day']].update(elem)

        dd = d.values()

        result = sorted(dd, key=lambda x: x['each_day'])

        print result

        #result = d.values()

        import json
        import decimal
        from django.db.models.base import ModelState

        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
               if hasattr(obj, 'isoformat'):
                   return obj.isoformat()
               elif isinstance(obj, decimal.Decimal):
                   return float(obj)
               elif isinstance(obj, ModelState):
                   return None
               else:
                   return json.JSONEncoder.default(self, obj)

        json_re = json.dumps(result, cls=DateTimeEncoder)

        return {
            'result': result,
            'users': users,
            'json_re': json_re
        }
    @method_decorator(permission_required('wanglibao_pay.change_payinfo', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):

        return super(MarketingView, self).dispatch(request, *args, **kwargs)

    def post(self, request):

        try:
            counts = int(request.POST.get('counts'))
        except:
            message = u'请输入合法的数字'
        else:
            MockGenerator.generate_codes(counts)
            message = u'生成 %s 条邀请码, 请点击<a href="/AK7WtEQ4Q9KPs8Io_zOncw/marketing/invitecode/" />查看</a>' % counts
        return HttpResponse({
            message
        })
