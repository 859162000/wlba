from django.conf import settings
from django.contrib.auth import get_user_model
from marketing.models import IntroducedBy


def set_promo_user(request, user):
    if user:
        user_id = request.session.get(settings.PROMO_TOKEN_USER_SESSION_KEY, None)
        if user_id:
            introduced_by_user = get_user_model().objects.get(pk=user_id)
            record = IntroducedBy()
            record.introduced_by = introduced_by_user
            record.user = user
            record.save()

            # Clean the session
            del request.session[settings.PROMO_TOKEN_USER_SESSION_KEY]




