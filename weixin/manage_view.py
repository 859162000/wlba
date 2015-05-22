# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from weixin.common.wechat import WeixinAccounts

class ManageView(TemplateView):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(ManageView, self).dispatch(request, *args, **kwargs)


class IndexView(ManageView):
    template_name = 'manage/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        host_url = '{}{}'.format(['http://', 'https://'][settings.ENV != settings.ENV_DEV], self.request.get_host())
        WeixinAccounts.host_url = host_url
        context['items'] = WeixinAccounts.all()
        return context


class AccountView(ManageView):
    template_name = 'manage/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountView, self).get_context_data(**kwargs)
        self.request.session['account_key'] = kwargs.get('account_key')
        return context


class MenuView(ManageView):
    template_name = 'manage/menu.html'

    def get_context_data(self, **kwargs):
        context = super(MenuView, self).get_context_data(**kwargs)

        return context






