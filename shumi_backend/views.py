from django.shortcuts import render
from django.views.generic import TemplateView, View
from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseServerError, HttpResponseBadRequest
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist

from models import ShumiProfile
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
            shumi_profile = ShumiProfile.objects.get(user=user)
        except ObjectDoesNotExist:
            return HttpResponseServerError('Can not fetch user with pk %s' % pk)
        #try if callback with expected params
        try:
            qs = self.request.GET
            oauth_token = qs['oauth_token']
            oauth_verifier = qs['oauth_verifier']
        except KeyError:
            return HttpResponseBadRequest('expect params oauth_token and oauth_verifier.')

        #try if token matched
        if oauth_token != shumi_profile.resource_owner_key:
            return HttpResponse('callback token not match')
        #save token and verifier
        shumi_profile.resource_owner_key = oauth_token
        shumi_profile.oauth_verifier = oauth_verifier
        shumi_profile.save()


        return HttpResponse('oauth token: %s <br>oauth_verifier: %s' % (oauth_token, oauth_verifier))



class OAuthView(View):
    """
    Generate ShumiProfile object, store unauthorized resource owner key/secret.
    """


class GetAuthorizeStatusView(OAuthView):

    def get(self, request, *args, **kwargs):
        user = request.user
        auth_status = ShumiProfile.objects.filter(user=user).exists()
        return HttpResponse(auth_status)

class OauthTriggerView(TemplateView):
    """

    """
    template_name = 'trigger.jade'

    def get_context_data(self, **kwargs):
        pass