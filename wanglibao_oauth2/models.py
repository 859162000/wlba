# coding=utf-8

"""
Default model implementations. Custom database or OAuth backends need to
implement these models with fields and and methods to be compatible with the
views in :attr:`provider.views`.
"""

from django.db import models
from django.conf import settings
from .utils import now, short_token, long_token
from .utils import get_token_expiry, deserialize_instance
from .managers import AccessTokenManager
from marketing.models import Channels

try:
    from django.utils import timezone
except ImportError:
    timezone = None

AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


class Client(models.Model):
    """
    Default client implementation.

    Expected fields:

    * :attr:`client_id`
    * :attr:`client_secret`
    * :attr:`channel_code`
    * :attr:`channel`

    Clients are outlined in the :rfc:`2` and its subsections.
    """

    client_id = models.CharField(u'客户端ID', unique=True, db_index=True, max_length=255, default=short_token)
    client_secret = models.CharField(u'客户端密钥', max_length=255, default=long_token)
    channel = models.ForeignKey(Channels, verbose_name=u'渠道', help_text=u'渠道', blank=True, null=True)
    reg_return_token = models.BooleanField(u'注册返回Token', default=False)
    created_time = models.DateTimeField(u'创建时间', auto_now=True)

    def __unicode__(self):
        return self.client_id

    def get_default_token_expiry(self):
        return get_token_expiry()

    def serialize(self):
        return dict(client_id=self.client_id,
                    client_secret=self.client_secret,
                    channel=self.channel.id)

    @classmethod
    def deserialize(cls, data):
        if not data:
            return None

        kwargs = {}

        # extract values that we care about
        for field in cls._meta.fields:
            name = field.name
            val = data.get(field.name, None)

            # handle relations
            if val and field.rel:
                val = deserialize_instance(field.rel.to, val)

            kwargs[name] = val

        return cls(**kwargs)


class AccessToken(models.Model):
    """
    Default access token implementation. An access token is a time limited
    token to access a user's resources.

    Access tokens are outlined :rfc:`5`.

    Expected fields:

    * :attr:`user`
    * :attr:`token`
    * :attr:`client` - :class:`Client`
    * :attr:`expires` - :attr:`datetime.datetime`

    Expected methods:

    * :meth:`get_expire_delta` - returns an integer representing seconds to
        expiry
    """
    user = models.ForeignKey(AUTH_USER_MODEL)
    token = models.CharField(max_length=255, default=long_token, db_index=True)
    client = models.ForeignKey(Client)
    expires = models.DateTimeField()

    objects = AccessTokenManager()

    def __unicode__(self):
        return self.token

    def save(self, *args, **kwargs):
        if not self.expires:
            self.expires = self.client.get_default_token_expiry()
        super(AccessToken, self).save(*args, **kwargs)

    def get_expire_delta(self, reference=None):
        """
        Return the number of seconds until this token expires.
        """
        if reference is None:
            reference = now()
        expiration = self.expires

        if timezone:
            if timezone.is_aware(reference) and timezone.is_naive(expiration):
                # MySQL doesn't support timezone for datetime fields
                # so we assume that the date was stored in the UTC timezone
                expiration = timezone.make_aware(expiration, timezone.utc)
            elif timezone.is_naive(reference) and timezone.is_aware(expiration):
                reference = timezone.make_aware(reference, timezone.utc)

        timedelta = expiration - reference
        return timedelta.days*86400 + timedelta.seconds


class RefreshToken(models.Model):
    """
    Default refresh token implementation. A refresh token can be swapped for a
    new access token when said token expi
    res.

    Expected fields:

    * :attr:`user`
    * :attr:`token`
    * :attr:`access_token` - :class:`AccessToken`
    * :attr:`client` - :class:`Client`
    * :attr:`expired` - ``boolean``
    """
    user = models.ForeignKey(AUTH_USER_MODEL)
    token = models.CharField(max_length=255, default=long_token)
    access_token = models.OneToOneField(AccessToken, related_name='refresh_token')
    client = models.ForeignKey(Client)
    expired = models.BooleanField(default=False)

    def __unicode__(self):
        return self.token
