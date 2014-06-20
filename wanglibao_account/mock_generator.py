from django.contrib.auth import get_user_model
from wanglibao_account.utils import create_user


class MockGenerator(object):
    @classmethod
    def generate_user(cls, clean=False):
        User = get_user_model()

        if clean:
            User.objects.all().filter(wanglibaouserprofile__phone__contains='10000000').delete()

        for i in range(0, 10):
            create_user('1000000%.4d' % i, 'wanglibank', 'user %d' % i)
