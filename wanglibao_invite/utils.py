# encoding: utf-8

import random
from weixin.util import getMiscValue

def iter_method(data):
    total = sum(data.values())
    rad = random.randint(1,total)

    cur_total = 0
    res = ""
    for k, v in data.items():
        cur_total += v
        if rad<= cur_total:
            res = k
            break
    return res

def getRandomRedpackId():
    # redpack_data = getMiscValue("redpack_rain")
    redpack_data = {'1': 20,'2': 30, '3': 40, '4': 10}
    redpack_id = int(iter_method(redpack_data))
    return redpack_id








