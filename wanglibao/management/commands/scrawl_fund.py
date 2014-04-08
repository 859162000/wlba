from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from wanglibao_robot import fund
import sys


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('--offset', type='int', default=0, help='Specify the offset, default is 0'),
    )

    def handle(self, *args, **options):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        offset = options['offset']
        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True


        fund.run_robot(clean, offset=offset)
