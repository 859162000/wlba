#!/usr/bin/env python
# encoding:utf-8

from .tasks import process_channel_product_push


process_channel_product_push.apply_async()
