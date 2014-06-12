from django.core.management.base import BaseCommand
from shumi_backend.fetch import AppInfoFetcher
from wanglibao_portfolio.mock_generator import MockGenerator
from wanglibao_robot import trust_robot
from wanglibao_robot import fund
from logging import getLogger
from shumi_backend.exception import FetchException
from datetime import datetime, timedelta


class Command(BaseCommand):

    def handle(self, *args, **options):
        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True

        #load portfolio
        MockGenerator.generate_products(clean)
        MockGenerator.load_portfolio_from_file('fixture/portfolio.csv', clean)

        #scrawl trust
        #trust_robot.run_robot(clean)

        #scrawl fund
        robot = fund.FundRobot()
        logger = getLogger('shumi')
        try:
            robot.sync_issuer()
        except FetchException, e:
            logger.error(e)

        try:
            robot.update_issuer()
        except FetchException:
            logger.error(e)

        try:
            robot.run_robot()
        except Exception, e:
            logger.error(e)

        #syncsm
        try:
            fetcher = AppInfoFetcher()
            print('Starting sync available cash funds.')
            fetcher.fetch_available_cash_fund()
            fetcher.sync_fund_and_available_fund()

            base = datetime.today()
            date_list = [(base-timedelta(days=x)).strftime('%Y-%m-%d') for x in range(0, 30)]
            for date in date_list:
                fetcher.fetch_monetary_fund_net_value(date)
        except Exception, e:
            logger.error(e)

