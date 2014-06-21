from django.contrib.auth.decorators import user_passes_test


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