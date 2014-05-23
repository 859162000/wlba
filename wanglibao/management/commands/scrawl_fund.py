from logging import getLogger
from django.core.management.base import BaseCommand, CommandError
from wanglibao_robot import fund
from shumi_backend.exception import FetchException

class Command(BaseCommand):


    def handle(self, *args, **options):
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
