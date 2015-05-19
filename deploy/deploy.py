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
    'lb': ["182.92.9.134", "112.126.76.220"],
    'web': ["182.92.167.178", "123.56.101.185"],
    'mq': ["182.92.104.171"],
    'pre': ["182.92.175.133"],
    'dbback': ["112.124.13.222"],

    'git_server': ["182.92.9.134"],
    'webback':["118.193.12.139"],
}
env.user = "wangli"
env.git_server_path = "~/wanglibao-backend"
env.deploy_path = "/var/www/wanglibao/wanglibao-backend"
env.deploy_virt_path = "/var/www/wanglibao/virt-wanglibao"
env.git_server_address = "git clone wangli@10.165.69.234:~/wanglibao-backend"
env.activate = "source %s/bin/activate" % env.deploy_virt_path
env.pip_install = "pip install -r %s/requirements.txt" % env.deploy_path
env.branch = "production5.0"

env.environment = 'ENV_PRODUCTION'
#env.environment = 'ENV_STAGING'

@roles('mq', 'pre')
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
@roles("web")
def deploy_web_action():
    if not exists(env.deploy_path):
        with cd("/var/www/wanglibao"):
            run(env.git_server_address)
    print yellow("backup last code")
    run("rm -rf %s-back" % env.deploy_path)
    run("cp -r %s %s-back" % (env.deploy_path, env.deploy_path))
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
            json_env = json.dumps({"BROKER_URL":"amqp://wanglibao:wanglibank@10.171.17.243/wanglibao"})
            put(StringIO(json_env), 'env.json')
            #如果为web01
            if hostname == "iZ25a8a8cn5Z":
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
        rs = run("ps aux|grep wanglibao|grep -v 'grep'")
        if rs.return_code > 0:
            put("super_web.ini", "~/super_web.ini")
            sudo("cp ~/super_web.ini /etc/supervisor/super_web.ini")
            sudo("supervisorctl reload")

@roles("lb")
def deploy_static_action():
    hostname = run("hostname")
    if not exists(env.deploy_path):
        with cd("/var/www/wanglibao"):
            #如果为lb01
            if hostname == "iZ25s4rr2pzZ":
                run("git clone ~/wanglibao-backend")
            else:
                run(env.git_server_address)
    with cd(env.deploy_path):
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
    with virtualenv():
        run(env.pip_install)

    with settings(warn_only=True):
        rs = run("ps aux|grep nginx|grep -v 'grep'")
        print yellow("check nginx daemon")
        if rs.return_code > 0:
            sudo("sudo /usr/local/nginx/sbin/nginx")
            run("ps aux|grep nginx")

@roles("lb")
def deploy_restart_nginx():
    put("www.wanglibao.com", "~/www.wanglibao.com")
    sudo("cp ~/www.wanglibao.com /usr/local/nginx/sites-enabled/www.wanglibao.com")
    with settings(warn_only=True):
        rs = run("ps aux|grep nginx|grep -v 'grep'")
        print yellow("check nginx daemon")
        if rs.return_code > 0:
            sudo("sudo /usr/local/nginx/sbin/nginx")
        else:
            sudo("sudo /usr/local/nginx/sbin/nginx -s reload")
        run("ps aux|grep nginx")

@roles("mq")
def deploy_mq_action():
    if not exists(env.deploy_path):
        with cd("/var/www/wanglibao"):
            run(env.git_server_address)
    print yellow("backup last code")
    run("rm -rf %s-back" % env.deploy_path)
    run("cp -r %s %s-back" % (env.deploy_path, env.deploy_path))
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
    with virtualenv():
        with hide("output"):
            run(env.pip_install)
        with cd(env.deploy_path):
            print yellow('Replacing wanglibao/settings.py ENV')
            run("fab config:'wanglibao/settings.py','ENV \= ENV_DEV','ENV \= %s'" % env.environment)
            json_env = json.dumps({"BROKER_URL":"amqp://wanglibao:wanglibank@10.171.17.243/wanglibao"})
            put(StringIO(json_env), 'env.json')
    print yellow("restart mq server")
    with settings(warn_only=True):
        rs = run("ps aux|grep supervisord|grep -v 'grep'")
        print yellow("view server process and check the process exists")
        if rs.return_code == 0:
            sudo("supervisorctl restart all")
        else:
            sudo("supervisord -c /etc/supervisord.conf")

        rs = run("ps aux|grep wanglibao|grep -v 'grep'")
        if rs.return_code > 0:
            put("super_task.ini", "~/super_task.ini")
            sudo("cp ~/super_task.ini /etc/supervisor/super_task.ini")
            sudo("supervisorctl reload")
        run("ps aux|grep python")

    print yellow("update crontab job")
    with cd("/var/www/wanglibao"):
        fund, income, info, cmd = config_crontab()
        put(StringIO(fund), 'scrawl_job')
        put(StringIO(income), 'sync_sm_income')
        put(StringIO(info), 'sync_sm_info')
        put(StringIO(cmd), '/tmp/tmp_tab')
        run("chmod +x scrawl_job")
        run("chmod +x sync_sm_income")
        run("chmod +x sync_sm_info")
        run("crontab /tmp/tmp_tab")


@roles("webback")
def deploy_webback():
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

    if not exists(env.deploy_path):
        with cd("/var/www/wanglibao"):
            run("git clone ~/wanglibao-backend")
    print yellow("backup last code")
    run("rm -rf %s-back" % env.deploy_path)
    run("cp -r %s %s-back" % (env.deploy_path, env.deploy_path))
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
    with virtualenv():
        with hide("output"):
            run(env.pip_install)
        with cd(env.deploy_path):
            print yellow('Replacing wanglibao/settings.py ENV')
            run("fab config:'wanglibao/settings.py','ENV \= ENV_DEV','ENV \= %s'" % env.environment)
            run("""fab config:'wanglibao/settings.py',"SIGN_HOST \= '10.171.17.243'","SIGN_HOST \= '182.92.104.171'" """)
            json_env = json.dumps({"BROKER_URL":"amqp://wanglibao:wanglibank@182.92.104.171/wanglibao"})
            put(StringIO(json_env), 'env.json')
    print yellow("restart webback server")
    with settings(warn_only=True):
        rs = run("ps aux|grep supervisord|grep -v 'grep'")
        print yellow("view server process and check the process exists")
        if rs.return_code == 0:
            sudo("supervisorctl restart all")
        else:
            sudo("supervisord -c /etc/supervisord.conf")
            run("ps aux|grep python")

        rs = run("ps aux|grep wanglibao|grep -v 'grep'")
        if rs.return_code > 0:
            put("super_web.ini", "~/super_web.ini")
            sudo("cp ~/super_web.ini /etc/supervisor/super_web.ini")

            put("super_task.ini", "~/super_task.ini")
            sudo("cp ~/super_task.ini /etc/supervisor/super_task.ini")
            sudo("supervisorctl reload")

    with settings(warn_only=True):
        rs = run("ps aux|grep nginx|grep -v 'grep'")
        print yellow("check nginx daemon")
        if rs.return_code > 0:
            sudo("/usr/local/nginx/sbin/nginx")
            run("ps aux|grep nginx")

@roles("webback")
def deploy_stop_webback():
    print yellow("stop webback server")
    with settings(warn_only=True):
        rs = run("ps aux|grep supervisord|grep -v 'grep'")
        print yellow("view server process and check the process exists")
        if rs.return_code == 0:
            sudo("supervisorctl stop all")
            run("ps aux|grep python")
    with settings(warn_only=True):
        rs = run("ps aux|grep nginx|grep -v 'grep'")
        print yellow("check nginx daemon")
        if rs.return_code == 0:
            sudo("/usr/local/nginx/sbin/nginx -s stop")
            run("ps aux|grep nginx")



def config_crontab():
    cron_str = """
#!/bin/bash
cd /var/www/wanglibao/
source virt-wanglibao/bin/activate
cd wanglibao-backend
"""
    fund_str = cron_str + """
#update fund
date >> /var/log/wanglibao/scrawl.log
python manage.py run_robot &>> /var/log/wanglibao/scrawl.log
python manage.py scrawl_fund &>> /var/log/wanglibao/scrawl.log
date >> /var/log/wanglibao/scrawl.log
"""
    income_str = cron_str + """
#update shumi income
date >> /var/log/wanglibao/sync_sm.log
python manage.py syncsm -i &>> /var/log/wanglibao/sync_sm.log
date >> /var/log/wanglibao/sync_sm_i.log
"""
    info_str = cron_str + """
#update shumi info
date >> /var/log/wanglibao/sync_sm.log
python manage.py syncsm -f &>> /var/log/wanglibao/sync_sm.log
python manage.py syncsm -m &>> /var/log/wanglibao/sync_sm.log
date >> /var/log/wanglibao/sync_sm_fm.log
"""
    cron_command = """
SHELL=/bin/bash
0 0 * * * /var/www/wanglibao/scrawl_job
0 */1 * * * /var/www/wanglibao/sync_sm_info >/dev/null 2>&1
0 18-23/1 * * * /var/www/wanglibao/sync_sm_income >/dev/null 2>&1
"""
    return fund_str, income_str, info_str, cron_command

#更新消息队列
def deploy_mq():
    execute(check_out)
    execute(deploy_mq_action)

#更新web服务器
def deploy_web():
    execute(check_out)
    execute(deploy_web_action)

#更新静态文件
def deploy_static():
    execute(check_out)
    execute(deploy_static_action)

#更新所有
def deploy_www():
    start = datetime.datetime.now()
    execute(check_out)
    execute(deploy_static_action)
    execute(deploy_web_action)
    execute(deploy_mq_action)
    end = datetime.datetime.now()
    print green("success in %s" % str(end-start).split(".")[0])
    print green("%s" % str(end).split(".")[0])

