#!/usr/bin/env python
# encoding:utf-8
import json


def iphone_update():
    dic = {"version":"1.0", "size":"2.0M", "update_time":"2014-11-13", "description":"1、修改Bug\\n2、提高性能\\n3、美化界面", "url":"", "force":"false"}
    return dic

def ipad_update():
    dic = {"version":"1.0", "size":"2.0M", "update_time":"2014-11-13", "description":"1、修改Bug\\n2、提高性能\\n3、美化界面", "url":""}
    return dic

def android_update():
    dic = {"version":"1.0", "size":"2.0M", "update_time":"2014-11-13", "description":"1、修改Bug\\n2、提高性能\\n3、美化界面", "url":""}
    return dic

if __name__ == "__main__":
    a = json.dumps(iphone_update(), ensure_ascii=False)
    print(a)
