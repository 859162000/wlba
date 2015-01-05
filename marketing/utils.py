# -*- coding: utf-8 -*-


from django.conf import settings
from django.contrib.auth import get_user_model
from marketing.models import IntroducedBy, PromotionToken, ClientData
import logging


logger = logging.getLogger('p2p')


def set_promo_user(request, user, invitecode=''):
    if user:
        if invitecode:
            recordpromo = PromotionToken.objects.filter(token=invitecode).first()
            if recordpromo:
                introduced_by_user = get_user_model().objects.get(pk=recordpromo.pk)
                save_introducedBy(user, introduced_by_user)
        else:
            user_id = request.session.get(settings.PROMO_TOKEN_USER_SESSION_KEY, None)
            if user_id:
                introduced_by_user = get_user_model().objects.get(pk=user_id)
                save_introducedBy(user, introduced_by_user)

                # Clean the session
                del request.session[settings.PROMO_TOKEN_USER_SESSION_KEY]

def save_introducedBy(user, introduced_by_user):
    record = IntroducedBy()
    record.introduced_by = introduced_by_user
    record.user = user
    record.save()


def save_client(request, phone, action):
    """
    保存客户端信息
    :param request: 客户端请求
    :param phone:   请求用户电话号码
    :param action:  动作，0表示注册，1表示购买
    :return:
    """

    version = request.DATA.get('version', '')
    userdevice = request.DATA.get('userDevice', '')
    network = request.DATA.get('network', '')
    channelid = request.DATA.get('channelId', '')
    try:
        c = ClientData(version=version, userdevice=userdevice, network=network, channelid=channelid,
                       phone=phone, action=action)
        c.save()
    except:
        logger.error(u"客户端信息失败，请检查参数")