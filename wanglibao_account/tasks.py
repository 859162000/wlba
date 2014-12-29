#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'rsj217'


from wanglibao.celery import app
from wanglibao_account.utils import CjdaoUtils
import requests


@app.task
def cjdao_callback(url, params):
    r = requests.get(url, params=params)

    print '#'*40
    print r.url
    print r.status_code
