import logging
from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils import timezone
from report.reports import ReportGenerator


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--monetary', '-m',
                    action='store_true',
                    dest='fetch_monetary_net_values',
                    default=False,
                    help='fetch monetary funds net value form shumi.'),
    )

    def handle(self, *args, **options):
        today = timezone.now().date() + timezone.timedelta(days=-2)
        timestamp_str = today.strftime('%Y %m %d 00 00 00')
        start_time = timezone.datetime.strptime(timestamp_str, '%Y %m %d %H %M %S')
        logger.info('Start generating reports for start time: %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
        print 'Start generating reports for start time: %s' % start_time.strftime('%Y-%m-%d %H:%M:%S')
        ReportGenerator.generate_reports(start_time=start_time)
