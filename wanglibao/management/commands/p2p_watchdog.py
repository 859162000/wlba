import logging
from django.core.management.base import BaseCommand
from wanglibao_p2p.trade import P2POperator


logger = logging.getLogger('p2p')


class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            P2POperator.watchdog()
        except Exception, e:
            logger.error(e)