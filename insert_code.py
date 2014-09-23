from django.db import IntegrityError
import string, random, logging
from marketing.models import InviteCode

def gen_code():
    salt = ''.join(random.sample(string.ascii_letters+string.digits, 6))
    return salt


def save_code(salt):
    try:
        invite_code = InviteCode.objects.create(code=salt)
        invite_code.save()
    except IntegrityError, e:
        logging.debug(e)
