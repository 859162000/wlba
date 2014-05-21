# encoding:utf-8
from urllib import urlencode
from django.views.generic import TemplateView, View, RedirectView

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from wanglibao_buy.models import FundHoldInfo, TradeInfo, TradeHistory
from wanglibao_buy.views import update_and_save_product_trade_info
from wanglibao_fund.models import Fund
from exception import FetchException, AccessException
from auth import ShuMiExchangeAccessToken, ShuMiRequestToken
from trade import TradeWithAutoLogin
from utility import UrlTools, purchase, redeem, mapping_trade_history
from fetch import UserInfoFetcher

# Create your views here.


class OAuthCallbackView(View):
    """
    Handle OAuth provider call back,
    take the resource owner's token and key as input parameters,
    save input to db and starting exchange access token process.
    """

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk', None)
        #try if user matched
        try:
            callback_user = get_user_model().objects.get(pk=pk)
        except ObjectDoesNotExist:
            return HttpResponseServerError('Can not fetch user with pk %s' % pk)
        #try if callback with expected params
        if callback_user != self.request.user:
            return HttpResponseBadRequest('callback user object do not match request user.')

        user = self.request.user
        profile = user.wanglibaouserprofile

        try:
            qs = request.GET
            oauth_token = qs['oauth_token']
            oauth_verifier = qs['oauth_verifier']
        except KeyError:
            return HttpResponseBadRequest('expect params oauth_token and oauth_verifier.')

        #try if token matched
        if oauth_token != profile.shumi_request_token:
            return HttpResponse('callback token not match')

        if not (profile.shumi_request_token and profile.shumi_request_token_secret):
            return HttpResponse('user do not have request token or secret')

        try:
            exchanger = ShuMiExchangeAccessToken(profile.shumi_request_token, profile.shumi_request_token_secret,
                                                 oauth_verifier)
            access_token, access_token_secret = exchanger.exchange_access_token()
        # todo add exception handler instead of raise it.
        except FetchException:
            return HttpResponseBadRequest('exchange failed.')

        profile.shumi_access_token = access_token
        profile.shumi_access_token_secret = access_token_secret
        profile.save()

        try:
            user_info_fetcher = UserInfoFetcher(user)
            user_info_fetcher.fetch_user_info()
        except AccessException:
            pass
        except FetchException:
            pass

        return HttpResponseRedirect(reverse('oauth-status-view'))


class OAuthStatusView(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        fund_code = self.request.GET.get('fund_code', '')
        action = self.request.GET.get('action', '')
        session = self.request.session
        if fund_code and action:
            self.request.session['fund_code'] = fund_code
            self.request.session['action'] = action
        elif 'fund_code' in session and 'action' in session:
            #fund_code = self.request.session['fund_code']
            #return_url = self.request.session['action']
            pass
        else:
            return HttpResponseBadRequest('get no fund_code and action in either request string or session')
        profile = self.request.user.wanglibaouserprofile
        # if user have access token and access token secret, redirect to trade view.
        if profile.shumi_access_token and profile.shumi_access_token_secret:
            self.pattern_name = 'broker-view'
        # if user have no token or secret, redirect to oauth view
        else:
            self.pattern_name = 'oauth-start-view'
        return super(OAuthStatusView, self).get_redirect_url(*args, **kwargs)


class BrokerView(View):

    def get(self, request, *args, **kwargs):
        try:
            fund_code = request.session['fund_code']
            action = request.session['action']
        except KeyError:
            return HttpResponseBadRequest('no fund code or action in session')

        if action == 'purchase':
            trade_url = purchase(fund_code)
        elif action == 'redeem':
            target_fund = FundHoldInfo.objects.filter(user__exact=self.request.user).filter(fund_code__exact=fund_code)
            if not target_fund.exists():
                return HttpResponseBadRequest('current user do not have fund %s.' % fund_code)
            target_fund = target_fund.first()
            share_type = target_fund.share_type
            trade_account = target_fund.trade_account
            usble_remain_share = target_fund.usable_remain_share

            trade_url = redeem(fund_code, share_type=share_type, trade_account=trade_account,
                               usable_remain_share=usble_remain_share)
        else:
            pass

        return_url = UrlTools(request).gen_trade_return_url()

        data = dict()
        data['trade_url'] = trade_url
        data['return_url'] = return_url

        redirect_url = reverse('trade-redirect-view') + '?' + urlencode(data)

        return HttpResponseRedirect(redirect_url)


class TradeView(View):

    def get(self, request, *args, **kwargs):

        try:
            trade_url = request.GET['trade_url']
            return_url = request.GET['return_url']

        except KeyError:
            # todo redirect to funds list view instead of raise error
            return HttpResponseBadRequest('no trade url or return url in request')

        profile = self.request.user.wanglibaouserprofile
        access_token = profile.shumi_access_token
        access_token_secret = profile.shumi_access_token_secret
        trader = TradeWithAutoLogin(access_token, access_token_secret,
                                    trade_url, return_url)
        return HttpResponseRedirect(trader.get_trade_auto_login_url())


class TradeCallbackView(TemplateView):

    template_name = 'shumi_callback.jade'
    def get_context_data(self, **kwargs):
        context = super(TradeCallbackView, self).get_context_data(**kwargs)
        try:
            order_id = self.request.GET['orderId']
        except KeyError:
            return context

        # get trade record from shumi
        try:
            record_obj = UserInfoFetcher(self.request.user).get_user_trade_history_by_serial(order_id)
        except FetchException:
            return context
        # store buy info
        item_id = Fund.objects.get(product_code=record_obj.fund_code).id
        if int(record_obj.amount) == 0:
            amount = record_obj.shares
        else:
            amount = record_obj.amount
        buy_info = TradeInfo(user=self.request.user, type='fund',
                             item_id=item_id, item_name=record_obj.fund_name,
                             amount=amount, verify_info=record_obj.apply_serial,
                             trade_type=record_obj.business_type_to_cn)

        update_and_save_product_trade_info(buy_info)

        action = ''
        if record_obj.business_type == '022':
            action = u'申购'
        else:
            action = u'赎回'

        return {
            'action': action,
            'record': record_obj
        }


class OAuthStartView(RedirectView):

    permanent = False

    # todo get hostname and schema from request.
    def get_redirect_url(self, *args, **kwargs):
        profile = self.request.user.wanglibaouserprofile
        helper = UrlTools(self.request)
        call_back_url = helper.gen_oauth_callback_url()
        requester = ShuMiRequestToken(call_back_url)
        request_token, request_token_secret = requester.get_request_token_secret()
        profile.shumi_request_token = request_token
        profile.shumi_request_token_secret = request_token_secret
        profile.save()
        self.url = requester.get_redirect_address()
        return super(OAuthStartView, self).get_redirect_url(*args, **kwargs)


