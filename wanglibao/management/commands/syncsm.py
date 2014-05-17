import logging
from optparse import make_option
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from shumi_backend.fetch import AppInfoFetcher
from wanglibao_fund.models import Fund
from shumi_backend.exception import FetchException, InfoLackException


logger = logging.getLogger('shumi')


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--monetary', '-m',
                    action='store_true',
                    dest='fetch_monetary_net_values',
                    default=False,
                    help='fetch monetary funds net value form shumi.'),
        make_option('--daily-income', '-i',
                    action='store_true',
                    dest='compute_daily_income',
                    default=False,
                    help='Compute user daily income.'),
        make_option('--available-cash-funds', '-f',
                    action='store_true',
                    dest='fetch_available_cash_funds',
                    default=False,
                    help='fetch shumi available cash funds'),
        make_option('--init-monetary-net-values', '-M',
                    action='store_true',
                    dest='init_monetary-net-values',
                    default=False,
                    help='fetch cash fund net value info from shumi for last 30 days.'
                    )
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
            except FetchException:
                print e
                logger.error(e)

        if options['fetch_monetary_net_values']:
            try:
                print('Starting sync monetary funds net values.')
                fetcher.fetch_monetary_fund_net_value()
            except FetchException, e:
                print e
                logger.error(e)

        if options['compute_daily_income']:
            try:
                print('Starting compute users daily income.')
                fetcher.compute_user_daily_income()
            except InfoLackException, e:
                print(e)
                logger.error(e)

        if options['init_monetary-net-values']:
            base = datetime.today()
            date_list = [(base-timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 30)]
            for date in date_list:
                fetcher.fetch_monetary_fund_net_value(date)
