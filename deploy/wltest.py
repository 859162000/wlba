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
    'lb': ["192.168.20.247"],
    'web': ["192.168.20.247"],
    'mq': ["192.168.20.247"],

    'wltest': ["192.168.20.247"],
    'git_server': ["192.168.20.231"],
    #'git_server': ["192.168.10.223"],
}
env.user = "wangli"
env.password = '52e6FJOd'
env.git_server_path = "~/wanglibao-backend"
env.deploy_path = "/var/www/wanglibao/wanglibao-backend"
env.deploy_virt_path = "/var/www/wanglibao/virt-wanglibao"
env.git_server_address = "git clone wangli@192.168.20.231:~/wanglibao-backend"
#env.git_server_address = "git clone wangli@192.168.10.223:~/wanglibao-backend"
env.activate = "source %s/bin/activate" % env.deploy_virt_path
env.pip_install = "pip install -r %s/requirements.txt" % env.deploy_path
env.branch = "master"

env.environment = 'ENV_STAGING'

env.redis_server = "192.168.20.247"
env.mq_server = "192.168.20.247"

@roles('mq')
def install_rabbitmq():
    sudo("apt-get update")
    sudo("apt-get install rabbitmq-server")
    users = sudo('rabbitmqctl list_users')
    if users.find('wanglibao') == -1:
        sudo('rabbitmqctl add_user wanglibao wanglibank')

    vhosts = sudo('rabbitmqctl list_vhosts')
    if vhosts.find('wanglibao') == -1:
        sudo('rabbitmqctl add_vhost wanglibao')
        sudo('rabbitmqctl set_permissions -p wanglibao wanglibao ".*" ".*" ".*"')

@roles("git_server")
def check_out():
    cd("~/")
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
    #with cd("/var/www/wanglibao"):
    with prefix("source %s/bin/activate" % env.deploy_virt_path):
        yield

#并行执行
#@parallel
@roles("wltest")
def deploy_web_action():
    if not exists(env.deploy_path):
        with cd("/var/www/wanglibao"):
            run(env.git_server_address)
    ##print yellow("backup last code")
    ##run("rm -rf %s-back" % env.deploy_path)
    ##run("cp -r %s %s-back" % (env.deploy_path, env.deploy_path))
    print yellow("update web code")
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
            run("fab config:'wanglibao/settings.py','192.168.1.242','192.168.20.247'")
            if hostname == "UBT020247":
                print yellow("syncdb")
                run("python manage.py syncdb --noinput")
                print yellow("migrate")
                run("python manage.py migrate")
    print yellow("restart web server")
    with settings(warn_only=True):
        rs = run("ps aux|grep supervisord|grep -v 'grep'")
        print yellow("view server process and check the process exists")
        if rs.return_code == 0:
            sudo("supervisorctl restart all")
        else:
            sudo("supervisord -c /etc/supervisord.conf")


#更新 web & task
def deploy_wltest():
    start = datetime.datetime.now()
    execute(check_out)
    execute(deploy_web_action)
    end = datetime.datetime.now()
    print green("success in %s" % str(end-start).split(".")[0])
    print green("%s" % str(end).split(".")[0])

