from django.db.models.signals import post_save
from django.contrib.auth.models import User
from models import WanglibaoUserProfile


def create_profile(sender, **kw):
    """
    Create the user profile when a user object is created
    """
    user = kw["instance"]
    if kw["created"]:
        profile = WanglibaoUserProfile(user=user)
        profile.save()

post_save.connect(create_profile, sender=User, dispatch_uid="users-profile-creation-signal")