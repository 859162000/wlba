#!/usr/bin/env python
# encoding:utf-8

import json
from StringIO import StringIO
from fabric.api import env, run, task, roles, cd, sudo, execute, parallel, prompt, prefix, put, hide, settings
from contextlib import contextmanager
from fabric.contrib.files import exists, contains
from fabric.colors import green, red, yellow

env.roledefs = {
    "staging": ["staging.wanglibao.com"]
}
env.user = "jinlong"
env.password = "jinlong"
env.root = "/home/jinlong/docker_image/"
env.environment = "ENV_STAGING"

who = env.get("who", "")

workers = {"lizhenjing":{"app":8051, "mysql":33051}, 
            #"hetao":{"app":8052, "mysql":33052}, 
            "lili":{"app":8053, "mysql":33053},
            "wangruyue":{"app":8054, "mysql":33054}, 
            "qifeifei":{"app":8055, "mysql":33055}, 
            "zhanghe":{"app":8056, "mysql":33056},
            "limengting":{"app":8057, "mysql":33057}, 
            "wangxiaoqing":{"app":8058, "mysql":33058}, 
            #"jinlong":{"app":8059, "mysql":33059},
            #"jianghao":{"app":8061, "mysql":33061},
            #"wangjianfei":{"app":8062, "mysql":33062},
            "huomeimei":{"app":8063, "mysql":33063},
            #"caowenhai":{"app":8064, "mysql":33064},
            "qijinjin":{"app":8065, "mysql":33065}}

@roles("staging")
def depoly_staging():
    if not who:
        print("please input your name!")
        return
    if who not in workers:
        print red("You are not in the work list, please contact the master!")
        return

    namepath = env.root + who
    if not exists(namepath):
        with cd(env.root):
            run("mkdir %s" % who)
    if not exists(namepath + "/log"):
        with cd(namepath):
            run("mkdir log")
    path = namepath + "/wanglibao-backend"
    if not exists(path):
        print green("Please input your repo url. Example:https://github.com/singpenguin/wanglibao-backend.git")
        url = raw_input("> :")
        if not url:
            print("Please input url")
            return
        with cd(namepath):
            print green("Please input your github username and password.")
            run("git clone %s" % url)
            print yellow('Replacing wanglibao/settings.py ENV')
            run("fab config:'wanglibao/settings.py','ENV \= ENV_DEV','ENV \= %s'" % env.environment)
            json_env = json.dumps({"BROKER_URL":"amqp://wanglibao:wanglibank@localhost/wanglibao"})
            put(StringIO(json_env), 'env.json')
    else:
        with cd(path):
            print green("Please input your github username and password.")
            run("git checkout wanglibao/settings.py")
            run("git checkout master")
            run("git pull origin master")
            print yellow('Replacing wanglibao/settings.py ENV')
            run("fab config:'wanglibao/settings.py','ENV \= ENV_DEV','ENV \= %s'" % env.environment)
            json_env = json.dumps({"BROKER_URL":"amqp://wanglibao:wanglibank@localhost/wanglibao"})
            put(StringIO(json_env), 'env.json')
    rs = sudo("docker ps -a")
    if who not in rs:
        sudo("docker run -d -p %s:8056 -p %s:3306 --name %s -v /home/jinlong/docker_image/%s:/root/wanglibao  -v /home/jinlong/docker_image/%s/log:/var/log/wanglibao wanglibao /bin/sh -c '/root/start.sh>/var/log/wanglibao/deploy.log;supervisord -n'" % (workers[who]["app"], workers[who]["mysql"], who, who, who))
    else:
        sudo("docker restart %s" % who)
