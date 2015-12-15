# encoding:utf-8
from __future__ import absolute_import
import os
import logging

from celery.app.task import Task
from django.conf import settings
from celery import Celery


logger = logging.getLogger(__name__)


class WangliTask(Task):
    abstract = True

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None,
                    link=None, link_error=None, **options):
        try:
            super(WangliTask, self).apply_async(args=args, kwargs=kwargs, connect_timeout=30, task_id=task_id,
                                                producer=producer, link=link, link_error=link_error, **options)
        except:
            logger.exception('send_task_failed_with_para:' + str(args) + str(kwargs))


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')
app = Celery('wanglibao', task_cls=WangliTask)
# app = Celery('wanglibao')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))