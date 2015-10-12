from wanglibao.celery import app
from .utils import send_messages as send_messages_impl
from wanglibao_sms.views import get_report_messages


@app.task
def send_messages(phones, messages, channel=1, ext=''):
    return send_messages_impl(phones, messages, channel=channel, ext=ext)


@app.task
def message_arrived_rate_task():
    get_report_messages()
