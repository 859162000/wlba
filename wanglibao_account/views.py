# encoding: utf-8
import datetime
import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import resolve_url
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import TemplateView
from registration.models import RegistrationProfile
from registration.views import RegistrationView
from django.core.mail import EmailMultiAlternatives

from forms import EmailOrPhoneRegisterForm, ResetPasswordGetIdentifierForm
from utils import generate_username, detect_identifier_type
from wanglibao_sms.utils import validate_validation_code, send_validation_code


logger = logging.getLogger(__name__)

User = get_user_model()


class RegisterView (RegistrationView):
    template_name = "register.jade"
    form_class = EmailOrPhoneRegisterForm

    def register(self, request, **cleaned_data):
        nickname = cleaned_data['nickname']
        password = cleaned_data['password']
        identifier = cleaned_data['identifier']
        identifier_type = detect_identifier_type(identifier)

        username = generate_username(identifier)

        # Use the model create model, call save later manually
        user = User(username=username)
        user.set_password(password)
        user.save()

        user.wanglibaouserprofile.nick_name = nickname
        user.wanglibaouserprofile.save()

        if identifier_type == 'email':
            user.email = identifier
            user.is_active = False
            registration_profile = RegistrationProfile.objects.create_profile(user)
            user.save()

            from_email, to = settings.DEFAULT_FROM_EMAIL, user.email
            context = {"activation_code": registration_profile.activation_key}

            subject = render_to_string('html/activation-title.html', context).strip('\n').encode('utf-8')
            text_content = render_to_string('html/activation-text.html', context).encode('utf-8')
            html_content = render_to_string('html/activation-html.html', context).encode('utf-8')

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
        if request.GET.get('next'):
            return request.GET.get('next')
        return u'/accounts/email/sent/'


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


class PasswordResetValidateView(TemplateView):
    template_name = 'password_reset_phone.jade'

    def post(self):
        pass


class PasswordResetGetIdentifierView(TemplateView):
    template_name = 'password_reset.jade'

    def post(self, request, **kwargs):
        form = ResetPasswordGetIdentifierForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            identifier_type = detect_identifier_type(identifier)

            users = None
            if identifier_type == 'email':
                users = User.objects.filter(email=identifier, is_active=True)
            elif identifier_type == 'phone':
                users = User.objects.filter(wanglibaouserprofile__phone=identifier, wanglibaouserprofile__phone_verified=True)

            # There should be at most one user found
            assert len(users) <= 1

            if len(users) == 0:
                return HttpResponse(u"找不到该用户", status=400)
            else:
                view = PasswordResetValidateView()
                view.request = request

                request.session['user_to_reset'] = users[0].id
                return view.render_to_response({
                    'user_to_reset': users[0]
                })
        else:
            return HttpResponse(form.errors, status=400)

    def get_context_data(self, **kwargs):
        return {
            'form': ResetPasswordGetIdentifierForm()
        }


def send_validation_mail(request, **kwargs):
    user_id = request.session['user_to_reset']
    user_email = get_user_model().objects.get(pk=user_id).email

    form = PasswordResetForm(data={
        'email': user_email
    })

    if form.is_valid():
        form.save(request=request)
        return HttpResponse(u'验证邮件已发送，请您登录邮箱完成验证')
    else:
        return HttpResponse(u'没有有效的邮箱地址', status=500)


def send_validation_phone_code(request, **kwargs):
    user_id = request.session['user_to_reset']
    user_phone = get_user_model().objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = send_validation_code(phone_number)

    return HttpResponse(
        str({"message": message}), status=status)


def validate_phone_code(request):
    logger.info("Enter validate_phone_code")
    validate_code = request.POST['validate_code']
    user_id = request.session['user_to_reset']
    user_phone = get_user_model().objects.get(pk=user_id).wanglibaouserprofile.phone
    phone_number = user_phone.strip()

    status, message = validate_validation_code(phone_number, validate_code)
    if status == 200:
        logger.debug("Phone code validated")
        request.session['phone_validated_time'] = (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds()
        return HttpResponse('validate code succeeded', status=200)

    logger.debug("Phone code not valid")
    try:
        del request.session['phone_validated_time']
    except KeyError:
        pass
    return HttpResponse(message, status=status)


class ResetPassword(TemplateView):
    template_name = "password_reset_set_password.jade"

    def post(self, request):
        password1 = request.POST['new_password1'].strip()
        password2 = request.POST['new_password2'].strip()

        if password1 != password2:
            return HttpResponse(u'两次密码不匹配', status=400)

        if 'user_to_reset' not in request.session:
            return HttpResponse(u'没有用户信息', status=500)

        user_id = request.session['user_to_reset']
        user = get_user_model().objects.get(pk=user_id)

        assert('phone_validated_time' in request.session)
        last_validated_time = request.session['phone_validated_time']
        assert(last_validated_time != 0)

        if (datetime.datetime.now() - datetime.datetime(1970, 1, 1)).total_seconds() - last_validated_time < 30 * 60:
            user.set_password(password1)
            user.save()
            return HttpResponseRedirect(redirect_to='/accounts/password/reset/done/')

        else:
            return HttpResponse(u'验证超时，请重新验证', status=400)

