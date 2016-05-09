#!/usr/bin/env python
# encoding:utf-8

import json
import datetime
from StringIO import StringIO
from fabric.api import env, run, task, roles, cd, sudo, execute, parallel, prompt, prefix, put, hide, settings
from contextlib import contextmanager
from fabric.contrib.files import exists, contains
from fabric.colors import green, red, yellow

env.roledefs = {
    #'lb': ["192.168.20.231"],
    #'web': ["192.168.20.232"],
    #'mq': ["192.168.20.233"],

    'git_server': ["192.168.20.231"],
    'channel': ["192.168.20.238"],
}
env.user = "wangli"
env.git_server_path = "~/channel/wanglibao-backend"
env.deploy_path = "/var/www/wanglibao/channel/wanglibao-backend"
env.deploy_virt_path = "/var/www/wanglibao/virt-wanglibao"
env.git_server_address = "git clone wangli@192.168.20.231:~/wanglibao-backend"
env.activate = "source %s/bin/activate" % env.deploy_virt_path
env.pip_install = "pip install -r %s/requirements.txt" % env.deploy_path
#env.branch = "production5.0"
env.branch = "chennel_center"
# env.branch = "master"

# env.environment = 'ENV_PRODUCTION'
# env.environment = 'ENV_STAGING'
env.environment = 'ENV_ALPHA'

env.redis_server = "192.168.20.233"
env.mq_server = "192.168.20.233"


@roles("git_server")
def check_out():
    with cd("~/channel"):
        print yellow("update git server")
        if not exists(env.git_server_path):
            run("git clone git@github.com:wanglibao/wanglibao-backend.git")
        else:
            with cd("wanglibao-backend"):
                run('git clean -f -d')
                with settings(warn_only=True):
                    result = run('git show-ref --verify --quiet refs/heads/%s' % env.branch)
                    if result.return_code > 0:
                        run('git fetch origin %s:%s' % (env.branch, env.branch))
                        run("git checkout %s" % env.branch)
                    else:
                        run('git checkout %s' % env.branch)
                        run('git pull origin %s' % env.branch)


@contextmanager
def virtualenv():
    # with cd("/var/www/wanglibao"):
    with prefix("source %s/bin/activate" % env.deploy_virt_path):
        yield


# 并行执行
# @parallel
@roles("channel")
def deploy_channel_action():
    if not exists(env.deploy_path):
        with cd("/var/www/wanglibao/channel"):
            run(env.git_server_address)
    print yellow("backup last code")
    run("rm -rf %s-back" % env.deploy_path)
    run("cp -r %s %s-back" % (env.deploy_path, env.deploy_path))
    print yellow("update channel code")
    with cd(env.deploy_path):
        run("git checkout wanglibao/settings.py")
        with settings(warn_only=True):
            result = run('git show-ref --verify --quiet refs/heads/%s' % env.branch)
            if result.return_code > 0:
                run('git fetch origin %s:%s' % (env.branch, env.branch))
                run("git checkout %s" % env.branch)
            else:
                run('git checkout %s' % env.branch)
                run('git pull origin %s' % env.branch)

    if not exists(env.deploy_virt_path):
        run("virtualenv %s" % env.deploy_virt_path)
    hostname = run("hostname")
    with virtualenv():
        with hide("output"):
            run(env.pip_install)
        with cd(env.deploy_path):
            print yellow('Replacing wanglibao/settings.py ENV')
            run("fab config:'wanglibao/settings.py','ENV \= ENV_DEV','ENV \= %s'" % env.environment)
            run("""fab config:'wanglibao/settings.py',"REDIS_HOST \= '127.0.0.1'",'REDIS_HOST \= "%s"' """%env.redis_server)
            run("fab config:'wanglibao/settings.py','staging.wanglibao.com','alpha.wanglibao.com'")
            run("fab config:'wanglibao/settings.py','qdtest.wanglibao.com','alpha-channel.wanglibao.com'")
            json_env = json.dumps({"BROKER_URL":"amqp://wanglibao:wanglibank@%s/wanglibao"%env.mq_server})
            put(StringIO(json_env), 'env.json')
            #如果为web01
            #if hostname == "iZ25a8a8cn5Z":
            if hostname == "ubu020238":
                print yellow("syncdb")
                run("python manage.py syncdb --noinput")
                print yellow("migrate")
                run("python manage.py migrate")
    print yellow("restart channel server")
    with settings(warn_only=True):
        rs = run("ps aux|grep supervisord|grep -v 'grep'")
        print yellow("view server process and check the process exists")
        if rs.return_code == 0:
            sudo("supervisorctl restart all")
        else:
            sudo("supervisord -c /etc/supervisord.conf")
        rs = run("ps aux|grep wanglibao|grep -v 'grep'")
        if rs.return_code > 0:
            #put("super_web.ini", "~/super_web.ini")
            #sudo("cp ~/super_web.ini /etc/supervisor/super_web.ini")
            sudo("supervisorctl reload")


# 更新web服务器
def deploy_channel():
    start = datetime.datetime.now()
    execute(check_out)
    execute(deploy_channel_action)
    end = datetime.datetime.now()
    print green("success in %s" % str(end-start).split(".")[0])
    print green("%s" % str(end).split(".")[0])

