from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from registration.backends.default.views import ActivationView
from forms import EmailOrPhoneAuthenticationForm
from views import RegisterView, PasswordResetGetIdentifierView, ResetPassword, EmailSentView
from django.contrib.auth import views as auth_views

urlpatterns = patterns(
    '',
    url(r'^home', login_required(TemplateView.as_view(template_name='account_home.jade'),
                                 login_url='/accounts/register/')),
    url(r'^bankcard', login_required(TemplateView.as_view(template_name='account_bankcard.jade'),
                                 login_url='/accounts/register/')),
    url(r'^login/', 'django.contrib.auth.views.login',
        {
            "template_name": "login.jade",
            "authentication_form": EmailOrPhoneAuthenticationForm,
        }, name="auth_login"),
    url(r'^register/$', RegisterView.as_view(), name='auth_register'),
    url(r'^email/sent/$', EmailSentView.as_view(), name='email_sent'),
    url(r'^favorite/', login_required(TemplateView.as_view(template_name='account_favorite.jade'),
                                      login_url='/accounts/register/')),
    url(r'^setting/', login_required(TemplateView.as_view(template_name='account_setting.jade'),
                                     login_url='/accounts/register/')),

    url(r'^password/change/$', "wanglibao_account.views.password_change", name='password_change'),
    url(r'^password/change/done/', TemplateView.as_view(template_name='html/password_change_done.html'),
        name='password_change_done'),
    url(r'^activate/complete/$',
        TemplateView.as_view(template_name='activation_complete.jade'),
        name='registration_activation_complete'),
    url(r'^activate/(?P<activation_key>\w+)/$',
                           ActivationView.as_view(template_name="activate.jade"),
                           name='registration_activate'),
    url(r'^password/reset/identifier/', PasswordResetGetIdentifierView.as_view(), name="password_reset"),
    url(r'^password/reset/validate/', PasswordResetGetIdentifierView.as_view(), name="password_reset_validate"),
    url(r'^password/reset/send_mail/', "wanglibao_account.views.send_validation_mail", name="send_validation_mail"),
    url(r'^password/reset/send_validate_code/', "wanglibao_account.views.send_validation_phone_code", name="send_validation_phone_code"),
    url(r'^password/reset/validate_phone_code/', "wanglibao_account.views.validate_phone_code"),
    url(r'^password/reset/set_password/', ResetPassword.as_view(), name="password_reset_set_password"),
    url(r'^password/reset/done/', TemplateView.as_view(template_name="password_reset_done.jade"), name="password_reset_done"),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
        auth_views.password_reset_confirm,
        {
            'post_reset_redirect': 'password_reset_done',
            'template_name': 'password_reset_confirm.jade',
        },
        name='auth_password_reset_confirm'),
    url(r'', include('registration.backends.default.urls')),
)