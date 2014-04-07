from django.core.management.base import BaseCommand, CommandError
from wanglibao_robot import bank_financing
import sys


class Command(BaseCommand):

    def handle(self, *args, **options):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True
        bank_financing.run_robot(clean)
