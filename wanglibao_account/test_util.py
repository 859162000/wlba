from django.contrib.auth.models import User
from marketing.models import InviteCode

__author__ = 'guoya'


def prepare_user(username = 'wanglibao_test_user'):
    InviteCode(code='3Cru4d', is_used=0).save()
    User(username=username).save()

def delete_user(username = 'wanglibao_test_user'):
    User.objects.filter(username=username).get().delete()

def has_user(username = 'wanglibao_test_user'):
    return User.objects.filter(username=username).exists()

def get_user(username = 'wanglibao_test_user'):
    return User.objects.filter(username=username).get()


