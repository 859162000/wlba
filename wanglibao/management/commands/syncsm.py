import logging
from optparse import make_option
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from shumi_backend.fetch import AppInfoFetcher
from wanglibao_fund.models import Fund


logger = logging.getLogger('shumi')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--monetary',
                    action='store_true',
                    dest='fetch_monetary_net_values',
                    default=False,
                    help='fetch monetary funds net value form shumi.'),
        make_option('--daily-income',
                    action='store_true',
                    dest='compute_daily_income',
                    default=False,
                    help='Compute user daily income.'),
        make_option('--available-cash-funds',
                    action='store_true',
                    dest='fetch_available_cash_funds',
                    default=False,
                    help='fetch shumi available cash funds')
    )
    def handle(self, *args, **options):
        try:
            fetcher = AppInfoFetcher()
        except Exception, e:
            logger.error(e)

        if options['fetch_available_cash_funds']:
            try:
                print('Starting sync available cash funds.')
                fetcher.fetch_available_cash_fund()
            except Exception, e:
                logger.error(e)

        if options['fetch_monetary_net_values']:
            try:
                print('Starting sync monetary funds net values.')
                fetcher.fetch_monetary_fund_net_value()
            except Exception, e:
                logger.error(e)

        if options['compute_daily_income']:
            try:
                print('Starting compute users daily income.')
                fetcher.compute_user_daily_income()
            except Exception, e:
                logger.error(e)

