#!/usr/bin/env python
# encoding:utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf8')

import pytz
import time
import datetime
import logging
import decimal
from django.utils import timezone
from django.db.models import Sum

logger = logging.getLogger(__name__)


def local_datetime(dt):
    return timezone.get_current_timezone().normalize(dt)


def stamp(dt):
    return long(time.mktime(local_datetime(dt).timetuple()))


