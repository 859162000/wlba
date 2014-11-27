# encoding:utf-8
import json
import decimal
from datetime import date, timedelta, datetime
from collections import defaultdict

from django.db.models import Count, Sum
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from wanglibao_p2p.models import P2PRecord
from django.views.generic import TemplateView
from django.http.response import HttpResponse
from mock_generator import MockGenerator
from django.conf import settings
from django.db.models.base import ModelState



# Create your views here.

class MarketingView(TemplateView):
    template_name = 'diary.jade'

    def get_context_data(self, **kwargs):

        start = self.request.GET.get('start', '')
        end = self.request.GET.get('end', '')
        if start and end:
            d0 = datetime.strptime(start, '%Y-%m-%d').date()
            d1 = datetime.strptime(end, '%Y-%m-%d').date()
        else:
            d0 = (datetime.now() - timedelta(days=7)).date()
            d1 = date.today()

        users = User.objects.filter(date_joined__range=(d0, d1)).order_by('each_day') \
            .extra({'each_day': 'date(date_joined)'}).values('each_day') \
            .annotate(joined_num=Count('id'))

        trades = P2PRecord.objects.filter(create_time__range=(d0, d1), catalog='申购').order_by('each_day') \
            .extra({'each_day': 'date(create_time)'}).values('each_day') \
            .annotate(trade_num=Count('id'), amount=Sum('amount'))

        d = defaultdict(dict)

        for l in (users, trades):
            for elem in l:
                d[elem['each_day']].update(elem)

        dd = d.values()

        result = sorted(dd, key=lambda x: x['each_day'])


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
            'json_re': json_re,
            'start': d0.strftime('%Y-%m-%d'),
            'end': d1.strftime('%Y-%m-%d')
        }

    @method_decorator(permission_required('marketing.change_sitedata', login_url='/' + settings.ADMIN_ADDRESS))
    def dispatch(self, request, *args, **kwargs):
        return super(MarketingView, self).dispatch(request, *args, **kwargs)


class GennaeratorCode(TemplateView):
    template_name = 'gennerator_code.jade'

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
