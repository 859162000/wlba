# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication
from weixin.common.decorators import weixin_api_error
from weixin.common.wx import get_host_url
from weixin.models import WeixinAccounts


class ManageAccountMixin(object):
    account_cache = None
    client_cache = None

    def get_account(self, account_key=None):
        try:
            account_key = account_key or self.request.session.get('account_key')
            account = WeixinAccounts.get(account_key)
            return account
        except:
            raise Http404()

    @property
    def account(self):
        if not self.account_cache:
            self.account_cache = self.get_account()
        return self.account_cache

    @property
    def client(self):
        if not self.client_cache:
            self.client_cache = self.account.weixin_client
        return self.client_cache


class ManageAPISessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        pass


class ManageAPIView(APIView, ManageAccountMixin):
    permission_classes = (IsAdminUser,)
    authentication_classes = (ManageAPISessionAuthentication,)


class ManageView(TemplateView, ManageAccountMixin):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ManageView, self).dispatch(request, *args, **kwargs)


class IndexView(ManageView):
    template_name = 'manage/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        WeixinAccounts.host_url = get_host_url(self.request)
        context['items'] = WeixinAccounts.all()
        if True:
            WeixinAccounts.syncdb()
        return context


class AccountView(ManageView):
    template_name = 'manage/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        self.request.session['account_key'] = kwargs.get('account_key')
        context['account'] = self.account

        return context


class MenuView(ManageView):
    template_name = 'manage/menu.html'

    def get_context_data(self, **kwargs):
        context = super(MenuView, self).get_context_data(**kwargs)
        context['account'] = self.account
        return context


class MenuApi(ManageAPIView):
    http_method_names = ['get', 'post', 'delete']

    @weixin_api_error
    def get(self, request):
        key = 'account_menu_{account_id}'.format(account_id=self.account.id)
        if not cache.get(key):
            res = self.client.menu.get()
            try:
                menu = res.get('menu')
            except:
                menu = {'button': []}

            cache.set(key, menu, 60 * 60 * 24 / 10000)
        return Response(cache.get(key))

    @weixin_api_error
    def post(self, request):
        res = self.client.menu.create(request.body)
        return Response(res, status=201)

    @weixin_api_error
    def delete(self, request):
        res = self.client.menu.delete()
        return Response(res, status=204)





