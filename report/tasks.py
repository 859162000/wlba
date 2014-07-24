# coding=utf-8
from django.utils import timezone
from celery.utils.log import get_task_logger
from report.reports import ReportGenerator
from wanglibao.celery import app

logger = get_task_logger(__name__)

@app.task
def generate_report():
    today = timezone.now().date() + timezone.timedelta(days=-1)
    timestamp_str = today.strftime('%Y %m %d 00 00 00')
    start_time = timezone.datetime.strptime(timestamp_str, '%Y %m %d %H %M %S')
    logger.info('Start generating reports for start time: %s' % start_time.strftime('%Y-%m-%d %H:%M:%S'))
    ReportGenerator.generate_reports(start_time=start_time)