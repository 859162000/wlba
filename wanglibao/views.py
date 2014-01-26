from registration.backends.default.views import RegistrationView


class RegisterView (RegistrationView):
    template_name = "register.html"