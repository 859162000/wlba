# encoding:utf-8
from django.shortcuts import render_to_response
from django.views.generic import View, RedirectView
from django.http import HttpResponse, HttpResponseForbidden, Http404, HttpResponseNotFound
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.urlresolvers import reverse
from weixin.wechatpy import WeChatClient, parse_message, create_reply
from weixin.wechatpy.replies import TransferCustomerServiceReply
from weixin.wechatpy.utils import check_signature
from weixin.wechatpy.exceptions import InvalidSignatureException
from weixin.wechatpy.oauth import WeChatOAuth
from .models import Account, WeixinUser
from .common.wechat import tuling
import json
import time
import uuid


class ConnectView(View):
    account = None

    def check_signature(self, request, id):
        try:
            self.account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            return False

        try:
            check_signature(
                self.account.token,
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

        # reply = create_reply(u'更多功能，敬请期待！', msg)
        if msg.type == 'text':
            if msg.content in ['dkf', 'DKF', 'Dkf' u'多客服']:
                reply = TransferCustomerServiceReply()
            else:
                reply = tuling(msg)
        else:
            reply = create_reply(u'更多功能，敬请期待！', msg)

        return HttpResponse(reply.render())

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(ConnectView, self).dispatch(request, *args, **kwargs)


class WeixinJsapiConfig(View):

    def get(self, request, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            return HttpResponse(json.dumps({'errcode': 1, 'errmsg': 'account does not exist'}), 'application/json')
        client = WeChatClient(account.app_id, account.app_secret, account.access_token)
        noncestr = uuid.uuid1().hex
        timestamp = str(int(time.time()))
        url = request.META.get('HTTP_REFERER')
        signature = client.jsapi.get_jsapi_signature(noncestr, account.jsapi_ticket, timestamp, url)
        data = {
            'app_id': account.app_id,
            'timestamp': timestamp,
            'nonceStr': noncestr,
            'signature': signature
        }
        return HttpResponse(json.dumps(data), 'application/json')


class WeixinLogin(View):

    def get(self, request):
        code = request.GET.get('code')
        if code:
            account_id = request.GET.get('state')
            try:
                account = Account.objects.get(pk=account_id)
            except Account.DoesNotExist:
                return HttpResponseNotFound()

            oauth = WeChatOAuth(account.app_id, account.app_secret)
            res = oauth.fetch_access_token(code)
            if not res.get('errcode'):
                account.oauth_access_token = res.get('access_token')
                account.oauth_access_token_expires_in = res.get('expires_in')
                account.oauth_refresh_token = res.get('refresh_token')
                account.save()
                WeixinUser.objects.get_or_create(openid=res.get('openid'))
                request.session['openid'] = res.get('openid')

        return render_to_response('register.html')

    def post(self, request):
        from django.contrib.auth import authenticate, login
        user = authenticate(identifier=request.POST.get('identifier'), password=request.POST.get('password'))
        if user:
            if not user.is_active:
                data = {'errcode': 1, 'errmsg': 'User account is disabled.'}
                return HttpResponse(json.dumps(data), 'application/json')

            if user.wanglibaouserprofile.frozen:
                data = {'errcode': 1, 'errmsg': 'User account is frozen.'}
                return HttpResponse(json.dumps(data), 'application/json')

            try:
                weixin_user = WeixinUser.objects.get(openid=request.session.get('openid'))
                weixin_user.user = user
                weixin_user.save()
            except WeixinUser.DoesNotExist:
                pass

            login(request, user)
            data = {'errcode': 0}
            return HttpResponse(json.dumps(data), 'application/json')

        data = {'errcode': 1, 'errmsg': 'login failed'}
        return HttpResponse(json.dumps(data), 'application/json')


class WeixinOauthLoginRedirect(RedirectView):

    def get_redirect_url(self, id, *args, **kwargs):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            raise Http404()

        oauth = WeChatOAuth(
            app_id=account.app_id,
            app_secret=account.app_secret,
            redirect_uri=self.request.build_absolute_uri(reverse('weixin_login')),
            scope='snsapi_base',
            state=str(account.id)
        )

        return oauth.authorize_url

