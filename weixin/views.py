# encoding:utf-8
from django.views.generic import View
from django.http import HttpResponse, HttpResponseForbidden
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Account
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException
from .common.wechat import tuling
# Create your views here.


class ConnectView(View):

    def check_signature(self, request, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            return False

        try:
            check_signature(
                account.token,
                request.GET.get('signature'),
                request.GET.get('timestamp'),
                request.GET.get('nonce')
            )
        except InvalidSignatureException:
            return False

        return True

    def get(self, request, id):
        if not self.check_signature(request, id):
            return HttpResponseForbidden()

        return HttpResponse(request.GET.get('echostr'))

    def post(self, request, id):
        if not self.check_signature(request, id):
            return HttpResponseForbidden()

        msg = parse_message(request.body)

        if msg.type == 'text':

            reply = tuling(msg)
        else:
            reply = create_reply(u'更多功能，敬请期待！', msg)

        return HttpResponse(reply.render())

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ConnectView, self).dispatch(request, *args, **kwargs)



