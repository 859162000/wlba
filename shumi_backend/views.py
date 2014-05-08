from django.views.generic import TemplateView, View, RedirectView
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse


from exception import FetchException
from auth import ShuMiExchangeAccessToken, ShuMiRequestToken

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

        return_url = request.session.get('trade_return_url', '')
        fund_code = request.session.get('trade_fund_code', '')
        # todo redirect to return url
        if not return_url:
            return_url = 'something'
        return HttpResponseRedirect(return_url)


class OAuthTriggerView(TemplateView):
    """

    """
    template_name = 'trigger.jade'

    def get_context_data(self, **kwargs):
        context = super(OAuthTriggerView, self).get_context_data(**kwargs)
        context['pageTitle'] = 'Test trigger'
        context['buyurl'] = 'http://www.baidu.com/'
        return context


class OAuthStatusView(RedirectView):

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        fund_code = self.request.get('fund_code', '')
        return_url = self.request.get('return_url', '')
        if fund_code and return_url:
            self.request.session['trade_fund_code'] = fund_code
            self.request.session['trade_return_url'] = return_url
        else:
            return HttpResponseBadRequest()
        profile = self.request.user.wanglibaouserprofile
        # if user have access token and access token secret, redirect to trade view.
        if profile.shumi_access_token and profile.shumi_access_token_secret:
            self.pattern_name = 'trade-view'
        # if user have no token or secret, redirect to oauth view
        else:
            self.pattern_name = 'oauth-start-view'
        return super(OAuthStatusView, self).get_redirect_url(*args, **kwargs)


class TradeView(TemplateView):

    template_name = 'trade.jade'

    def get_context_data(self, **kwargs):
        context = super(TradeView, self).get_context_data(**kwargs)
        context['oauth_uri'], context['oauth_body'] = ''

        # todo oauth sign function
        return context


class OAuthStartView(RedirectView):

    permanent = False

    # todo get hostname and schema from request.
    def get_redirect_url(self, *args, **kwargs):
        profile = self.request.user.wanglibaouserprofile
        #host = request.get_host()
        host = 'https://www.wanglibao.com'
        path = reverse('oauth-callback-view', kwargs={'pk': self.request.user.pk})
        requester = ShuMiRequestToken(host+path)
        request_token, request_token_secret = requester.get_request_token_secret()
        profile.shumi_request_token = request_token
        profile.shumi_request_token_secret = request_token_secret
        profile.save()
        self.url = requester.get_redirect_address()
        return super(OAuthStartView, self).get_redirect_url(*args, **kwargs)


