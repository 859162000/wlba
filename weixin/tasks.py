#!/usr/bin/env python
# encoding:utf-8
from celery.utils.log import get_task_logger

from django.forms import model_to_dict
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from order.models import Order
from order.utils import OrderHelper

from wanglibao.celery import app
from wanglibao_margin.marginkeeper import MarginKeeper
from wanglibao_p2p.models import P2PProduct, P2PRecord, Earning, ProductAmortization, ProductType
from wanglibao_p2p.trade import P2POperator
from wanglibao_p2p.automatic import Automatic
from django.db.models import Sum, Q
from django.contrib.auth.models import User
from wanglibao_sms import messages
from wanglibao_sms.tasks import send_messages
from wanglibao_account import message as inside_message
from wanglibao.templatetags.formatters import period_unit
import time, datetime

@app.task
def detect_product_biding():

    pass