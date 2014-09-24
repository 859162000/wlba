from django.db import IntegrityError
import string, random, logging
from marketing.models import InviteCode

logging.basicConfig(level=logging.DEBUG)

def gen_code():
    salt = ''.join(random.sample(string.ascii_letters+string.digits, 6))
    return salt


def save_code(salt):
    try:
        invite_code = InviteCode.objects.create(code=salt)
        invite_code.save()
        return True
    except IntegrityError, e:
        logging.debug(e)
        return False

def main():
    count = 0
    while count <= 1000:
        salt = gen_code()
        if save_code(salt):
            count += 1
    logging.debug('code inserted has been done')

if __name__ == '__main__':

    main()

