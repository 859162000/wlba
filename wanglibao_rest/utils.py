#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

def search(client, string):
    pattern = re.compile(client)
    return re.search(pattern, string)


