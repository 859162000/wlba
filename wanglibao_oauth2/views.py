# encoding: utf-8

import json
import StringIO
import traceback
import logging
from datetime import timedelta

from django.contrib.auth.tokens import default_token_generator
from rest_framework.views import APIView

from . import AccessTokenBaseView
from .models import AccessToken, RefreshToken
from .forms import RefreshTokenGrantForm, UserAndClientForm
from .utils import now
from .tools import get_current_utc_timestamp, generate_oauth2_sign
import constants
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def create_access_token(user, client):
    token = default_token_generator.make_token(user)
    return AccessToken.objects.create(user=user, client=client, token=token)


class AccessTokenView(AccessTokenBaseView):
    """
    Platform Open Api -- User Token View.
    """
    authentication = ()

    def get_refresh_token_grant(self, request, data, client):
        # 校验刷新令牌
        token = None
        form_errors = None
        data['client'] = client
        form = RefreshTokenGrantForm(data)
        if form.is_valid():
            token = form.cleaned_data['refresh_token']
        else:
            form_errors = form.errors

        return token, form_errors

    def create_refresh_token(self, request, user, access_token, client):
        return RefreshToken.objects.create(
            user=user,
            access_token=access_token,
            client=client
        )

    def get_access_token(self, request, user, client):
        try:
            # Attempt to fetch an existing access token.
            at = AccessToken.objects.get(user=user, client=client, expires__gt=now())
        except AccessToken.DoesNotExist:
            # None found... make a new one!
            at = create_access_token(user, client)
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

        logger.info("enter AccessTokenView with data[%s] grant_type[%s]" % (request.session, grant_type))

        if constants.ENFORCE_SECURE and not request.is_secure():
            response_data = {
                'code': 10100,
                'msg': 'A secure connection is required'
            }
            return HttpResponse(json.dumps(response_data), status=400, content_type='application/json')

        req_data = request.session if request.GET.get('promo_token') else request.POST
        form = UserAndClientForm(req_data)
        if form.is_valid() and form.check_sign():
            user = form.cleaned_data['user']
            client = form.cleaned_data['client']

            handler = self.get_handler(grant_type)

            try:
                response_data = handler(request, request.session, client, user)
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
            response_data = {
                'code': 30001,
                'msg': form.errors.values()[0][0]
            }

        return HttpResponse(json.dumps(response_data), status=200, content_type='application/json')


class AccessTokenOauthView(APIView):
    permission_classes = ()

    def post(self, request):
        data = request.POST
        token = data.get('access_token', None)
        client_id = data.get('client_id', '')
        user_id = data.get('user_id', '')
        utc_timestamp = data.get('time', '')
        sign = data.get('sign', None)
        channel = data.get('channel', '')
        logger.info("enter AccessTokenOauthView with data: %s" % data)
        if token and client_id and user_id and utc_timestamp and sign and channel:
            key = getattr(settings, '%s_OAUTH_KEY' % channel.upper(), None)
            if key:
                try:
                    if (int(get_current_utc_timestamp()) - int(utc_timestamp)) <= 120000:
                        if sign == generate_oauth2_sign(user_id, client_id, utc_timestamp, key):
                            access_token = AccessToken.objects.filter(token=token, expires__gte=timezone.now())
                            if access_token.exists():
                                utc_timestamp = get_current_utc_timestamp()
                                response_data = {
                                    'user_id': user_id,
                                    'client_id': client_id,
                                    'time': utc_timestamp,
                                    'sign': generate_oauth2_sign(user_id, client_id, int(utc_timestamp)-50, key),
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
                    else:
                        response_data = {
                            'ret_code': 10002,
                            'message': u'无效时间戳',
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
