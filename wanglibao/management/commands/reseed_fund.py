from optparse import make_option
from random import randrange
from django.core.management.base import BaseCommand
from wanglibao_fund.models import Fund


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (
        make_option('-c', '--clean', action="store_true", dest="clean", default=False),
    )

    def handle(self, *args, **options):
        for f in Fund.objects.all():
            f.bought_count_random = randrange(101, 121)/100.0
            f.bought_amount_random = randrange(90, 131)/100.0
            f.save()