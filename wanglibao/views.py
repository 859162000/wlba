import hashlib
import random
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import resolve_url
from django.template.loader import get_template, render_to_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from registration.models import RegistrationProfile
from registration.views import RegistrationView
from rest_framework.renderers import JSONRenderer
from wanglibao.forms import EmailOrPhoneRegisterForm
from wanglibao_hotlist.models import HotTrust, HotFund, HotFinancing
from wanglibao_hotlist.serializers import HotTrustSerializer, HotFundSerializer, HotFinancingSerializer
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao.utils import generate_username, detect_identifier_type
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template


User = get_user_model()


class RegisterView (RegistrationView):
    template_name = "html/register.html"
    form_class = EmailOrPhoneRegisterForm

    def register(self, request, **cleaned_data):
        username = cleaned_data['username']
        password = cleaned_data['password']
        identifier = cleaned_data['identifier']
        identifier_type = detect_identifier_type(identifier)

        if identifier_type == 'unknown':
            # TODO raise a proper exception
            return None

        if not username:
            username = generate_username(identifier)

        # Use the model create model, call save later manually
        user = User(username=username)
        user.set_password(password)
        user.save()

        if identifier_type == 'email':
            user.email = identifier
            user.is_active = False
            registration_profile = RegistrationProfile.objects.create_profile(user)
            user.save()

            # TODO make hard code values into settings
            from_email, to = 'noreply@wanglibao.com', user.email
            activation_code = registration_profile.activation_key

            context = {"activation_code": registration_profile.activation_key}

            subject = render_to_string('html/activation-title.html', context).encode('utf-8')
            text_content = render_to_string('html/activation-text.html', context).encode('utf-8')
            html_content = render_to_string('html/activation-html.html', context).encode('utf-8')

            subject = subject.strip('\n')
            email = EmailMultiAlternatives(subject, text_content, from_email, [to])
            email.attach_alternative(html_content, "text/html")
            email.send()

        elif identifier_type == 'phone':
            profile = user.wanglibaouserprofile
            profile.phone = identifier
            profile.phone_verified = True
            profile.save()

            # User already validated by phone, so he is an active user
            user.is_active = True
            user.save()

        return user

    def get_success_url(self, request=None, user=None):
        return u'/'


class IndexView(TemplateView):
    template_name = 'index.jade'

    def get_context_data(self, **kwargs):
        json = JSONRenderer()
        hot_trusts = HotTrust.objects.all()[:6]
        hot_funds = HotFund.objects.all()[:6]
        hot_financings = HotFinancing.objects.all()[:6]

        return {
            'hot_trusts': hot_trusts,
            'hot_funds': hot_funds,
            'hot_financings': hot_financings
            }


class AccountSettingView(TemplateView):
    pass



@sensitive_post_parameters()
@csrf_protect
@login_required
def password_change(request,
                    post_change_redirect=None,
                    password_change_form=PasswordChangeForm,
                    extra_context=None):
    if post_change_redirect is None:
        post_change_redirect = reverse('password_change_done')
    else:
        post_change_redirect = resolve_url(post_change_redirect)
    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(post_change_redirect)
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)

    # TODO find a proper status value and return error message
    return HttpResponse(status=400)
