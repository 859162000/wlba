import codecs
from django.core.management.base import BaseCommand, CommandError
from wanglibao_robot import bank_financing, trust_robot
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


class Command(BaseCommand):

    def handle(self, *args, **options):
        sys.stdout = codecs.getwriter("utf-8")(sys.stdout)

        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True
        bank_financing.run_robot(clean)
        trust_robot.run_robot(clean)
