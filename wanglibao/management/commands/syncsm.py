import logging
from optparse import make_option
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from shumi_backend.fetch import AppInfoFetcher
from wanglibao_fund.models import Fund


logger = logging.getLogger('shumi')


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            fetcher = AppInfoFetcher()
            fetcher.fetch_available_cash_fund()
        except Exception, e:
            logger.error(e)

