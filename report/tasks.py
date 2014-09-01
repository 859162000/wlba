# coding=utf-8
from django.utils import timezone
from celery.utils.log import get_task_logger
from report.reports import ReportGenerator
from wanglibao.celery import app

logger = get_task_logger(__name__)

@app.task
def generate_report(days=-2):
    today = timezone.now().date() + timezone.timedelta(days=days)
    timestamp_str = today.strftime('%Y %m %d 00 00 00')
    start_time = timezone.datetime.strptime(timestamp_str, '%Y %m %d %H %M %S')
    end_time = timezone.datetime.now()
    ReportGenerator.generate_reports(start_time=start_time, end_time=end_time)