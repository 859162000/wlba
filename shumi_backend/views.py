from urllib import urlencode
from django.views.generic import TemplateView, View, RedirectView

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from exception import FetchException
from auth import ShuMiExchangeAccessToken, ShuMiRequestToken
from trade import TradeWithAutoLogin
from utility import UrlTools, purchase

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
            user = get_user_model().objects.get(pk=pk)
            profile = user.wanglibaouserprofile
        except ObjectDoesNotExist:
            return HttpResponseServerError('Can not fetch user with pk %s' % pk)
        #try if callback with expected params
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

        return HttpResponseRedirect(reverse('oauth-status-view'))


class OAuthTriggerView(TemplateView):
    """

    """
    template_name = 'trigger.jade'

    def get_context_data(self, **kwargs):
        profile = self.request.user.wanglibaouserprofile
        context = super(OAuthTriggerView, self).get_context_data(**kwargs)
        trade_helper = UrlTools(self.request)
        data = dict()
        data['fund_code'] = '202301'
        data['return_url'] = trade_helper.gen_trade_return_url()
        oauth_redirect_base_url = reverse('oauth-status-view')

        context['pageTitle'] = 'Test trigger'
        context['buyurl'] = oauth_redirect_base_url + '?' + urlencode(data)
        return context


class OAuthStatusView(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        fund_code = self.request.GET.get('fund_code', '')
        return_url = self.request.GET.get('return_url', '')
        session = self.request.session
        if fund_code and return_url:
            self.request.session['fund_code'] = fund_code
            self.request.session['return_url'] = return_url
        elif 'fund_code' in session and 'return_url' in session:
            #fund_code = self.request.session['fund_code']
            #return_url = self.request.session['return_url']
            pass
        else:
            return HttpResponseBadRequest('get no fund_code and return in either request string or session')
        profile = self.request.user.wanglibaouserprofile
        # if user have access token and access token secret, redirect to trade view.
        if profile.shumi_access_token and profile.shumi_access_token_secret:
            self.pattern_name = 'trade-redirect-view'
        # if user have no token or secret, redirect to oauth view
        else:
            self.pattern_name = 'oauth-start-view'
        return super(OAuthStatusView, self).get_redirect_url(*args, **kwargs)


class TradeView(View):

    def get(self, request, *args, **kwargs):

        try:
            fund_code = self.request.session['fund_code']
            return_url = self.request.session['return_url']
        except KeyError:
            # todo redirect to funds list view instead of raise error
            return HttpResponseBadRequest('no fund code or return url in session')

        action = self.request.GET.get('action', 'buy')

        trade_url = purchase(fund_code)
        profile = self.request.user.wanglibaouserprofile
        access_token = profile.shumi_access_token
        access_token_secret = profile.shumi_access_token_secret
        trader = TradeWithAutoLogin(access_token, access_token_secret,
                                    trade_url, return_url)
        return HttpResponseRedirect(trader.get_trade_url())


class TradeCallbackView(View):

    def get(self, request, *args, **kwargs):
        try:
            order_id = self.request.GET['orderId']
        except KeyError:
            # todo show some fail info
            return HttpResponseBadRequest('No orderId')

        # todo store order id or fetch order detail
        return HttpResponse('order id is %s ' % order_id)


class OAuthStartView(RedirectView):

    permanent = False

    # todo get hostname and schema from request.
    def get_redirect_url(self, *args, **kwargs):
        profile = self.request.user.wanglibaouserprofile
        #host = request.get_host()
        #host = 'https://www.wanglibao.com'
        #path = reverse('oauth-callback-view', kwargs={'pk': self.request.user.pk})
        helper = UrlTools(self.request)
        call_back_url = helper.gen_oauth_callback_url()
        requester = ShuMiRequestToken(call_back_url)
        request_token, request_token_secret = requester.get_request_token_secret()
        profile.shumi_request_token = request_token
        profile.shumi_request_token_secret = request_token_secret
        profile.save()
        self.url = requester.get_redirect_address()
        return super(OAuthStartView, self).get_redirect_url(*args, **kwargs)


