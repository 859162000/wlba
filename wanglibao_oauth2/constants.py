from datetime import timedelta
from django.conf import settings


EXPIRE_DELTA = getattr(settings, 'OAUTH_EXPIRE_DELTA', timedelta(seconds=10 * 60))

# Remove expired tokens immediately instead of letting them persist.
DELETE_EXPIRED = getattr(settings, 'OAUTH_DELETE_EXPIRED', True)

ENFORCE_SECURE = getattr(settings, 'OAUTH_ENFORCE_SECURE', False)
ENFORCE_CLIENT_SECURE = getattr(settings, 'OAUTH_ENFORCE_CLIENT_SECURE', True)

SESSION_KEY = getattr(settings, 'OAUTH_SESSION_KEY', 'oauth')

SINGLE_ACCESS_TOKEN = getattr(settings, 'OAUTH_SINGLE_ACCESS_TOKEN', True)
