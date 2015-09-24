from django.contrib.auth.models import User
from marketing.models import InviteCode
from wanglibao_pay.models import Card, Bank
from wanglibao_profile.models import WanglibaoUserProfile


def prepare_user(username = 'wanglibao_test_user'):
    InviteCode(code='3Cru4d', is_used=0).save()
    user = User(username=username)
    user.save()
    return user

def prepare_user_with_profile(username='wanglibao_test_user'):
    user = prepare_user(username=username)
    profile = WanglibaoUserProfile(user_id=user.id, id_number='123456')
    profile.save()
    bank = Bank(name='test_bank')
    bank.save()
    card = Card(no='123456', user=user, bank=bank)
    card.save()
    return profile

def delete_user(username = 'wanglibao_test_user'):
    User.objects.filter(username=username).get().delete()

def has_user(username = 'wanglibao_test_user'):
    return User.objects.filter(username=username).exists()

def get_user(username = 'wanglibao_test_user'):
    return User.objects.filter(username=username).get()

def clear_db(*models):
    for model in models:
        model.objects.all().delete()


