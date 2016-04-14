#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.db import models
from common.tools import now


class AccessTokenManager(models.Manager):
    def get_token(self, token):
        return self.get(token=token, expires__gt=now())
