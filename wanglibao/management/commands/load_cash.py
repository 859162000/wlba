from optparse import make_option
from django.core.management.base import BaseCommand
import sys
from wanglibao_robot import cash


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-c', '--clean', action="store_true", dest="clean", default=False),
    )

    def handle(self, *args, **options):
        reload(sys)
        sys.setdefaultencoding('utf-8')

        cash.load_cash_from_file('fixture/cash_data.txt', clean=options['clean'])
        cash.scrawl_cash()
