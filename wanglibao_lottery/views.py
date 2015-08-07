# encoding=utf-8
import traceback
from django.http.response import HttpResponse
from rest_framework import renderers
from rest_framework.filters import DjangoFilterBackend
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from wanglibao.permissions import IsAdminUserOrReadOnly
from wanglibao_lottery.lotterytrade import LotteryTrade


class LotteryList(ListAPIView):
    model = LotteryTrade
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('user_id',)

class LotteryDetail(RetrieveAPIView):
    model = LotteryTrade
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('id',)

class LotteryIssue(APIView):
    """
    出票回调
    从零彩网传过来的参数：orderId，status，gameId，moneyType
                    ballNo，issueNo，sign
    """
    permission_classes = ()

    def get(self, request):
        print 'request %s'%request
        data = {
                'lottery_id': request.GET.get('orderId'),
                'bet_number': request.GET.get('ballNo'),
                'issue_number': request.GET.get('issueNo'),
                #下列参数没有被后端使用，只是传递到后端做校验
                'status': request.GET.get('status'),
                'gameId': request.GET.get('gameId'),
                'moneyType': request.GET.get('moneyType')
            }
        try:
            sign = request.GET.get('sign')
            lottery = LotteryTrade().issue(data, sign)
            if lottery:
                result = {
                    'orderId': data['lottery_id'],
                    'result': 1,
                }
            else:
                raise ValueError('lottery failed to  issue %s'%data['lottery_id'])
        except :
            traceback.print_exc()
            result = {
                    'orderId': data['lottery_id'],
                    'result': 2,
            }
        finally:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))


class LotteryOpen(APIView):
    """
    开奖回调
    从零彩网传递的参数：orderId，issueNo，gameId，rewardMoney，prizeMoney
                    prizeNo，prizeLevel，prizeMoneyAfterTax，tax，sign
    """
    permission_classes = ()

    def get(self, request):
        try:
            data = {
                'lottery_id': request.GET.get('orderId'),
                'win_number': request.GET.get('prizeNo'),
                'prize': request.GET.get('prizeMoneyAfterTax'),
                #下列参数没有被后端使用，只是传递到后端做校验
                'issueNo': request.GET.get('issueNo'),
                'gameId': request.GET.get('gameId'),
                'rewardMoney': request.GET.get('rewardMoney'),
                'prizeMoney': request.GET.get('prizeMoney'),
                'prizeLevel': request.GET.get('prizeLevel'),
                'tax': request.GET.get('tax'),
            }
            sign = self.request.GET.get('sign')
            lottery = LotteryTrade().open(data, sign)
            if lottery:
                result = {
                    'orderId': data['lottery_id'],
                    'result': 1,
                }
            else:
                raise ValueError('lottery failed to  open %s'%data['lottery_id'])
        except:
            traceback.print_exc()
            result = {
                    'orderId': data['lottery_id'],
                    'result': 2,
            }
        finally:
            return HttpResponse(renderers.JSONRenderer().render(result, 'application/json'))




