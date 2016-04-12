# encoding:utf-8

from django.conf import settings
import base64
from weixin.util import createInvite
from wanglibao_invite.tasks import processShareInviteDailyReward

class ShareInviteRegister(object):
    def __init__(self, request):
        self.request = request
        self.share_invite_key = settings.SHARE_INVITE_KEY

    def save_to_session(self):

        fphone = self.request.GET.get(self.share_invite_key, None)
        if fphone:
            self.request.session[self.share_invite_key] = fphone

    def clear_session(self):
        self.request.session.pop(self.share_invite_key, None)

    def process_for_register(self, user, openid):
        """
        用户可以在从渠道跳转后的注册页使用邀请码，优先考虑邀请码
        """
        self.save_to_introduceby(user)

        self.register_call_back(user, openid)
        self.clear_session()

    def save_to_introduceby(self, user):
        """
        处理使用邀请码注册的用户
        """
        if not user:
            return
        fphone = self.request.session.get(settings.SHARE_INVITE_KEY, None)
        if fphone:
            freind_phone = base64.b64decode(fphone + '=')
            createInvite(freind_phone, self.request.user)
            self.request.session[settings.PROMO_TOKEN_QUERY_STRING] = None


    def register_call_back(self, user, openid):
        """
        :param user:
        :return:
        """
        pass
