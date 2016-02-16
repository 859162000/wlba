from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse


def account_not_frozen(function=None):
    """
    Ensure the view is protected from frozen account

    :param function: The view function
    :return:
    """
    actual_decorator = user_passes_test(
        lambda u: not u.wanglibaouserprofile.frozen,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    """
    override login_required()
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated() and not u.wanglibaouserprofile.frozen,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def check_login_frozen(u):
    if u.is_authenticated():
        if u.wanglibaouserprofile.frozen:
            return HttpResponseRedirect(reverse('accounts_frozen'))
        else:
            return True
    else:
        return False
