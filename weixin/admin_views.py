# encoding:utf-8
from __future__ import unicode_literals
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import Http404
from .models import Account
from wechatpy.client import WeChatClient

class AdminTemplateView(TemplateView):

    @method_decorator(staff_member_required)
    def dispatch(self, request, *args, **kwargs):
        return super(AdminTemplateView, self).dispatch(request, *args, **kwargs)


class AdminWeixinTemplateView(AdminTemplateView):

    def get_account(self, id):
        try:
            account = Account.objects.get(pk=id)
        except Account.DoesNotExist:
            raise Http404('page not found')
        return account


class WeixinView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_manage.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)
        print account.jsapi_ticket

        return {
            'account': account
        }


class WeixinMassView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_mass.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)

        return {
            'account': account
        }


class WeixinReplyView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_reply.html'

    def get_context_data(self, id, **kwargs):

        account = self.get_account(id)

        return {
            'account': account
        }


class WeixinMenuView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_menu.html'

    def get_context_data(self, id, **kwargs):

        account = self.get_account(id)

        return {
            'account': account
        }


class WeixinMediaView(AdminWeixinTemplateView):

    template_name = 'admin/weixin_media.html'

    def get_context_data(self, id, **kwargs):
        account = self.get_account(id)
        return {
            'account': account
        }
