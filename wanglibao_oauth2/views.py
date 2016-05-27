# encoding: utf-8

import json
import logging
import StringIO
import traceback
from datetime import timedelta
from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView

import constants
from common.tools import get_utc_timestamp, now
from wanglibao_account.cooperation import CoopSessionProcessor
from .base_views import AccessTokenBaseView
from .models import AccessToken, RefreshToken, CoopToken
from .forms import RefreshTokenGrantForm, UserAndClientForm
from .utils import generate_oauth2_sign

logger = logging.getLogger(__name__)


class AccessTokenView(AccessTokenBaseView):
    """
    Platform Open Api -- User Token View.
    """
    authentication = ()

    def get_refresh_token_grant(self, request, data, client):
        # 校验刷新令牌
        token = None
        form_errors = None
        data['client_id'] = client.client_id
        form = RefreshTokenGrantForm(data)
        if form.is_valid():
            token = form.cleaned_data['refresh_token']
        else:
            form_errors = form.errors

        return token, form_errors

    def create_access_token(self, request, user, client):
        token = default_token_generator.make_token(user)
        return AccessToken.objects.create(user=user, client=client, token=token)

    def create_refresh_token(self, request, user, access_token, client):
        return RefreshToken.objects.create(
            user=user,
            access_token=access_token,
            client=client
        )

    def create_coop_token(self, coop_token, user, access_token, client):
        return CoopToken.objects.create(
            user=user,
            access_token=access_token,
            client=client,
            token=coop_token,
        )

    def get_access_token(self, request, user, client):
        try:
            # Attempt to fetch an existing access token.
            at = AccessToken.objects.get(user=user, client=client, expires__gt=now())
        except AccessToken.DoesNotExist:
            # None found... make a new one!
            at = self.create_access_token(request, user, client)
            self.create_refresh_token(request, user, at, client)

        return at

    def invalidate_refresh_token(self, rt):
        if constants.DELETE_EXPIRED:
            rt.delete()
        else:
            rt.expired = True
            rt.save()

    def invalidate_access_token(self, at):
        if constants.DELETE_EXPIRED:
            at.delete()
        else:
            at.expires = now() - timedelta(days=1)
            at.save()

    def post(self, request, grant_type):
        """
        As per :rfc:`3.2` the token endpoint *only* supports POST requests.
        """

        logger.info("enter AccessTokenView with data [%s], [%s] grant_type[%s]" % (request.REQUEST,
                                                                                   request.body, grant_type))

        if constants.ENFORCE_SECURE and not request.is_secure():
            response_data = {
                'code': 10100,
                'msg': 'A secure connection is required'
            }
            return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')

        req_data = request.session if request.GET.get('promo_token') else request.POST
        form = UserAndClientForm(req_data)
        if form.is_valid():
            user = form.cleaned_data['user']
            client = form.cleaned_data['client']

            handler = self.get_handler(grant_type)

            try:
                response_data = handler(request, request.session, client, user)
                response_data['msg'] = response_data['message']
                response_data.pop('message')
            except:
                # 创建内存文件对象
                fp = StringIO.StringIO()
                traceback.print_exc(file=fp)
                error_msg = fp.getvalue()
                logger.info("AccessTokenView raise error: %s" % error_msg)
                response_data = {
                    'code': 50001,
                    'msg': 'api error'
                }
        else:
            error_msg = form.errors.values()[0][0]
            channel_code = req_data.get('channel_code') or req_data.get('promo_token')
            if error_msg == u'无效手机号' and channel_code == 'bajinshe':
                default_invalid_token = settings.DEFAULT_INVALID_TOKEN
                response_data = {
                    'access_token': default_invalid_token,
                    'expires_in': 599,
                    'p2pUserId': req_data.get('channel_user'),
                    'refresh_token': default_invalid_token,
                    'code': 10000,
                    'message': 'success',
                }
            else:
                response_data = {
                    'code': 30001,
                    'msg': form.errors.values()[0][0]
                }

        CoopSessionProcessor(request).all_processors_for_session(1)
        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')


class AccessTokenOauthView(APIView):
    permission_classes = ()

    def post(self, request):
        data = request.POST
        token = data.get('access_token', None)
        client_id = data.get('client_id', '')
        user_id = data.get('user_id', '')
        sign = data.get('sign', None)
        channel = data.get('channel', '')
        logger.info("enter AccessTokenOauthView with data: %s" % data)
        if token and client_id and user_id and sign and channel:
            key = getattr(settings, '%s_OAUTH_KEY' % channel.upper(), None)
            if key:
                try:
                    if sign == generate_oauth2_sign(user_id, client_id, key):
                        access_token = AccessToken.objects.filter(Q(token=token, user_id=user_id) &
                                                                  (Q(expires__gte=now()) |
                                                                   Q(client__token_expire_switch=False)))
                        if access_token.exists():
                            response_data = {
                                'user_id': user_id,
                                'client_id': client_id,
                                'sign': generate_oauth2_sign(user_id, client_id, key),
                                'ret_code': 10000,
                                'message': 'success',
                            }
                        else:
                            response_data = {
                                'ret_code': 10003,
                                'message': u'token不存在',
                            }
                    else:
                        response_data = {
                            'ret_code': 10004,
                            'message': u'无效签名',
                        }
                except Exception, e:
                    logger.info("AccessTokenOauthView raise error: %s" % e)
                    response_data = {
                        'ret_code': 50002,
                        'message': 'api error',
                    }
            else:
                response_data = {
                    'ret_code': 10001,
                    'message': u'无效channel',
                }
        else:
            response_data = {
                'ret_code': 50001,
                'message': u'非法请求',
            }

        logger.info("AccessTokenOauthView process result: %s" % response_data["message"])

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')
