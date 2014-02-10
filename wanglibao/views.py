import hashlib
import random
from django.contrib.auth import get_user_model, login
from django.template.loader import get_template, render_to_string
from registration.models import RegistrationProfile
from registration.views import RegistrationView
from wanglibao.forms import EmailOrPhoneRegisterForm
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao.utils import generate_username
from django.core.mail import EmailMultiAlternatives
from django.template import Context, Template


User = get_user_model()

class RegisterView (RegistrationView):
    template_name = "register.html"
    form_class = EmailOrPhoneRegisterForm

    def register(self, request, **cleaned_data):

        username = cleaned_data['username']
        password = cleaned_data['password']
        identifier = cleaned_data['identifier']
        identifier_type = cleaned_data['type']

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

            subject = render_to_string('activation-title.html', context).encode('utf-8')
            text_content = render_to_string('activation-text.html', context).encode('utf-8')
            html_content = render_to_string('activation-html.html', context).encode('utf-8')

            subject = subject.strip('\n')
            email = EmailMultiAlternatives(subject, text_content, from_email, [to])
            email.attach_alternative(html_content, "text/html")
            email.send()

        elif identifier_type == 'phone':
            profile = user.wanglibaouserprofile
            profile.phone = identifier
            profile.phone_verified = True
            profile.save()

        user.backend = "Backend: AutoLoginAfterAuthenticate"
        login(request, user)
        return user

    def get_success_url(self, request=None, user=None):
        return u'/'


