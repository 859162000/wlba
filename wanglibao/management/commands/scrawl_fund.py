from django.core.management.base import BaseCommand, CommandError
from wanglibao_robot import fund
import sys


class Command(BaseCommand):

    def handle(self, *args, **options):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True
        fund.run_robot(clean)
