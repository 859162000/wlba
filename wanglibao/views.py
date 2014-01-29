from django.contrib.auth import get_user_model, login
from registration.views import RegistrationView
from wanglibao.forms import EmailOrPhoneRegisterForm
from wanglibao_profile.models import WanglibaoUserProfile
from wanglibao.utils import generate_username

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

        user = User.objects.create(username=username)
        user.set_password(password)
        user.save()

        if identifier_type == 'email':
            user.email = identifier
            user.is_active = False
            user.save()
            # TODO Trigger send activation mail by utilizing registration library

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
