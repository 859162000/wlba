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

workers = {"lizhenjing":8051, "hetao":8052, "lili":8053,
            "wangruyue":8054, "qifeifei":8055, "zhanghe":8056,
            "limengting":8057, "wangxiaoqing":8058, "jinlong":8059}

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
        #sudo("docker run -d -p %s:8056 --name %s -v /home/jinlong/docker_image/%s:/root/wanglibao wanglibao /bin/sh -c '/root/start.sh;supervisord -n'" % (workers[who], who, who))
        sudo("docker run -d -p %s:8056 --name %s -v /home/jinlong/docker_image/%s:/root/wanglibao /home/jinlong/docker_image/%s/log:/var/log/wanglibao wanglibao /bin/sh -c '/root/start.sh;supervisord -n'" % (workers[who], who, who, who))
    else:
        sudo("docker restart %s" % who)
