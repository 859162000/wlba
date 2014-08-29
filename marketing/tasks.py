# coding=utf-8
from celery.utils.log import get_task_logger
from django.db.models import Sum
from marketing.models import TimelySiteData
from wanglibao.celery import app
from wanglibao_margin.models import Margin

logger = get_task_logger(__name__)

@app.task
def generate_site_data():
    result = Margin.objects.aggregate(p2p_margin=Sum('margin'), freeze_amount=Sum('freeze'))

    data = TimelySiteData()
    data.p2p_margin = result.get('p2p_margin', 0)
    data.freeze_amount = result.get('freeze_amount', 0)
    data.total_amount = data.p2p_margin + data.freeze_amount
    data.user_count = Margin.objects.all().count()

    data.save()
