from django.db.models.signals import post_save
from django.contrib.auth.models import User
from models import UserMargin

def create_user_margin(sender, **kwargs):
    """
    create user margin after user object created.
    :param sender:
    :param kwargs:
    :return:
    """
    if kwargs['created']:
        user = kwargs['instance']
        margin = UserMargin(user=user)
        margin.save()


post_save.connect(create_user_margin, sender=User, dispatch_uid='users-margin-creation-signal')
