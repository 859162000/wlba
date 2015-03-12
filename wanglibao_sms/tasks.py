from wanglibao.celery import app
from .utils import send_messages as send_messages_impl

@app.task
def send_messages(phones, messages, channel=1):
    return send_messages_impl(phones, messages, channel=channel)
