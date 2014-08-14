from contextlib import contextmanager
import os
from StringIO import StringIO
from timeit import reindent
from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists, contains
from fabric_components.folder import create_folder
from fabric_components.apache import install_apache
from fabric_components.mysql import install_mysql, db_env, create_database, create_user, apt_get
from config.nginx_conf import generate_conf

env.apache_conf = 'config/apache.conf'
env.nginx_listen_on_80 = True

def production():
    env.host_string = 'www.wanglibao.com'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'production2.0'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = False

    env.mysql = False  # Use RDS, so we no need to install mysql


def pre_production():
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = False

    env.mysql = False


def dev():
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = True

    env.mysql = True


def staging():
    env.user = 'deploy'
    env.password = 'wanglibank'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = True

    env.mysql = True
    env.nginx_listen_on_80 = False


if env.get('group') == 'staging':
    env.roledefs = {
        'lb': ['staging.wanglibao.com'],
        'web': ['staging.wanglibao.com'],
        'task_queue': ['staging.wanglibao.com'],
        'db': ['staging.wanglibao.com'],
        'old_lb': [],
        'old_web': [],
        'cron_tab': ['staging.wanglibao.com'],
    }
    staging()

elif env.get('group') == 'production':
    env.roledefs = {
        'old-lb': [],
        'lb': ['pre.wanglibao.com'],
        'old-web': ['www.wanglibao.com'],
        'web': ['pre.wanglibao.com'],
        'task_queue': ['pre.wanglibao.com']
    }
    production()

elif env.get('group') == 'dev':
    env.roledefs = {
        # Old lb is the load balancer which points to old version, it should take out of the new webs
        'old_lb': [
            #'192.168.1.161'
        ],

        # New lb is the load balancer which points to new version, it should only with new web
        'lb': ['192.168.1.159'],

        # Old web is the server running with old version, they should not be touched
        'old_web': [
            '192.168.1.184'
        ],

        # Web is the server to be deployed with new version
        'web': [
            '192.168.1.160',
        ],

        # Cron tab is the server with crontab running. NOTE: The crontab should be with new version, and only
        # one crontab server should be running at the same time.
        'cron_tab': ['192.168.1.184'],

        # DB is the db servers
        'db': [
            #'192.168.1.161'
        ],

        # Task queue server is the server running rabbitmq or redis.
        'task_queue': ['192.168.1.184']
    }
    dev()

elif env.get('group') == 'pre':
    env.roledefs = {
        # Old lb is the load balancer which points to old version, it should take out of the new webs
        'old_lb': [
            #'192.168.1.161'
        ],

        # New lb is the load balancer which points to new version, it should only with new web
        'lb': ['115.28.80.27'],

        # Old web is the server running with old version, they should not be touched
        'old_web': [
        ],

        # Web is the server to be deployed with new version
        'web': [
            '115.28.240.194',
        ],

        # Cron tab is the server with crontab running. NOTE: The crontab should be with new version, and only
        # one crontab server should be running at the same time.
        'cron_tab': ['115.28.240.194'],

        # DB is the db servers
        'db': [
            # '115.28.240.194'
        ],

        # Task queue server is the server running rabbitmq or redis.
        'task_queue': ['115.28.240.194']
    }
    pre_production()


def new_virtualenv():
    with cd(env.path):
        sudo(env.pip_install_command + " virtualenv")
        if not exists('virt-python'):
            run("virtualenv virt-python")


@contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield


@task
def config(filename, key, value):
    """
    This method generate the files by replace key with value
    """
    config_file = open(filename)
    content = ''.join(config_file.readlines())
    content = content.replace(key, value)
    config_file.close()

    config_file = open(filename, 'w')
    config_file.write(content)
    config_file.close()


def add_cron_tab(job_file, job_log_file, env, period_string, manage_py, manage_actions, _start=False, _end=False):

    print green('Starting add cronjob %s, job log file in  %s' % (job_file, job_log_file))

    sudo('echo "#!/bin/bash" > %s' % job_file)
    sudo('echo %s &>> %s' % (env.activate, job_file))
    sudo('echo "date >> %s" >> %s' % (job_log_file, job_file))
    sudo('echo "cd /var/wsgi/wanglibao/" >> %s' % job_file)
    for action in manage_actions:
        sudo('echo "python %s %s &>> %s">> %s' % (manage_py, action, job_log_file, job_file))
    sudo('echo "date >> %s" >> %s' % (job_log_file, job_file))
    sudo('chmod +x %s' % job_file)
    if _start:
        sudo('echo "SHELL=/bin/bash" > /tmp/tmp_tab')
    sudo('echo "%s %s >/dev/null 2>&1" >> /tmp/tmp_tab' % (period_string, job_file))
    if _end:
        sudo('crontab /tmp/tmp_tab')


@task
@roles('task_queue')
def install_rabbit_mq():
    apt_get('software-properties-common', 'python-software-properties')

    if not contains('/etc/apt/sources.list', 'rabbitmq'):
        sudo("add-apt-repository \"deb http://www.rabbitmq.com/debian/ testing main\"")
        run("wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc")
        sudo("apt-key add rabbitmq-signing-key-public.asc")
        sudo("apt-get update")

    apt_get("rabbitmq-server")


@task
@roles('old_lb', 'lb', 'db', 'old_web', 'web')
def init():
    """
    Setup the server for the first time
    :return:
    """

    banner("init")
    with hide("output"):
        if not env.get('no-apt-update'):
            sudo('apt-get update')

        create_folder(env.path, mod="777")
        create_folder('/var/run/wanglibao/', owner='www-data', group='www-data', mod='770')
        create_folder('/var/log/wanglibao/', owner='www-data', group='www-data', mod='770')

        run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        put('deployment', '~/.ssh/id_rsa')
        run('chmod 600 ~/.ssh/id_rsa')

        apt_get("git")
        apt_get('supervisor')
        apt_get("gcc", "python-setuptools", "python-all-dev", "libpq-dev", "libjpeg-dev")
        sudo("easy_install pip")
        new_virtualenv()

        if env.host_string in env.roledefs['web'] or env.host_string in env.roledefs['old_web']:
            install_apache(mods=['headers', 'rewrite'], disable_mods=['ssl'], disable_sites=['default'])

            me = run('whoami')
            sudo('adduser %s www-data' % me)

            apt_get('libfreetype6-dev')

            apt_get('libxml2-dev', 'libxslt1-dev')
            apt_get('swig')
            apt_get('libmysqlclient-dev')

        if env.host_string in env.roledefs['db']:
            env.root_password = 'wanglibank'
            env.database = 'wanglibao'
            env.database_user = 'wanglibao'
            env.database_password = 'wanglibank'

            install_mysql(server=True, client=True)
            create_database()
            create_user()

        if env.host_string in env.roledefs['lb'] or env.host_string in env.roledefs['old_lb']:
            if not contains('/etc/apt/sources.list', 'nginx'):
                sudo('echo "deb http://ppa.launchpad.net/nginx/stable/ubuntu $(lsb_release -cs) main" >> /etc/apt/sources.list')
                sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv-keys C300EE8C')
                sudo("apt-get update")
            apt_get('nginx')
            put("vender/nginx_util/*",  "/usr/bin/", use_sudo=True, mode="770")

        if env.host_string in env.roledefs['task_queue']:
            install_rabbit_mq()


@task
@roles('lb')
def generate_nginx_conf():
    print green('Generate the nginx conf file for new lb')
    conf_content = generate_conf(apps=env.roledefs['web'], listen_on_80=env.nginx_listen_on_80)
    put(StringIO(conf_content), "/etc/nginx/sites-available/wanglibao-proxy.conf", use_sudo=True)
    sudo('rm -f /etc/nginx/sites-enabled/*')
    sudo('nginx_ensite wanglibao-proxy.conf')


@task
@roles('old_lb')
def take_out_of_rotation():
    banner('Generate the nginx conf file for old lb')
    conf_content = generate_conf(apps=env.roledefs['old_web'])
    put(StringIO(conf_content), "/etc/nginx/sites-available/wanglibao-proxy.conf", use_sudo=True)
    with settings(warn_only=True):
        sudo('nginx_dissite default')
    sudo('nginx_ensite wanglibao-proxy.conf')


@task
@roles('lb', 'web', 'db')
def check_out():
    banner("check out")
    with cd(env.path):
        if not exists(os.path.join(env.path, env.depot_name)):
            print green('Git folder not there, create it')
            run("git clone %s" % env.depot)
            sudo("chmod 777 %s" % env.depot_name)
            with cd(env.depot_name):
                run("git checkout %s" % env.branch)
        else:
            with cd(env.depot_name):
                with settings(warn_only=True):
                    run('git reset --hard HEAD')
                    run('git remote set-url origin %s' % env.depot)

                    result = run('git show-ref --verify --quiet refs/heads/%s' % env.branch)
                    if result.return_code > 0:
                        run('git fetch origin %s:%s' % (env.branch, env.branch))
                        run("git checkout %s" % env.branch)
                    else:
                        run('git checkout %s' % env.branch)
                        run('git pull origin %s' % env.branch)


@roles('cron_tab')
def setup_cron_tab():
    with cd(env.path):
        scrawl_job_file = '/usr/bin/scrawl_job'
        manage_py = '/var/wsgi/wanglibao/manage.py'
        log_file = '/var/log/wanglibao/scrawl.log'

        sync_sm_info = '/usr/bin/sync_sm_info'
        sync_sm_income = '/usr/bin/sync_sm_income'
        sync_sm_log = '/var/log/wanglibao/sync_sm.log'

        sudo('echo "#!/bin/bash" > %s' % scrawl_job_file)
        sudo('echo %s &>> %s' % (env.activate, scrawl_job_file))
        sudo('echo "date > %s" >> %s' % (log_file, scrawl_job_file))
        sudo('echo "cd /var/wsgi/wanglibao/" >> %s' % scrawl_job_file)
        sudo('echo "python %s %s &>> %s">> %s' % (manage_py, 'run_robot', log_file, scrawl_job_file))
        sudo('echo "python %s %s &>> %s">> %s' % (manage_py, 'scrawl_fund', log_file, scrawl_job_file))
        sudo('echo "date >> %s" >> %s' % (log_file, scrawl_job_file))
        sudo('chmod +x %s' % scrawl_job_file)
        sudo('echo "SHELL=/bin/bash" > /tmp/tmp_tab')
        sudo('echo "0 0 * * * %s" >> /tmp/tmp_tab' % scrawl_job_file)
        sudo('crontab /tmp/tmp_tab')

        add_cron_tab(sync_sm_info, sync_sm_log, env, '0 */1 * * *', manage_py, ['syncsm -f', 'syncsm -m'])
        add_cron_tab(sync_sm_income, sync_sm_log, env, '0 18-23/1 * * *', manage_py, ['syncsm -i'], _end=True)

        print green('Start the supervisor in daemon mode')

        with virtualenv():
            with cd('/var/wsgi/wanglibao'):
                if exists('/var/run/wanglibao/supervisor.pid'):
                    run("python manage.py supervisor stop all")
                    sudo("kill `cat /var/run/wanglibao/supervisor.pid`")
                run("python manage.py supervisor --daemonize --logfile=/var/log/wanglibao/supervisord.log --pidfile=/var/run/wanglibao/supervisor.pid")
                run("python manage.py supervisor update")
                run("python manage.py supervisor restart all")



@roles('web')
def config_apache():
    banner("config apache")
    with virtualenv():
        with cd(os.path.join(env.path, env.depot_name)):

            with hide('output'):
                run(env.pip_install)

                print green("Generate config file for the environment")
                if env.production:
                    print yellow('Replacing wanglibao/settings.py PRODUCTION')
                    run("fab config:'wanglibao/settings.py','PRODUCTION \= False','PRODUCTION \= True'")
                if not env.debug:
                    print yellow('Replacing wanglibao/settings.py DEBUG')
                    run("fab config:'wanglibao/settings.py','DEBUG \= True','DEBUG \= False'")
                if env.staging:
                    print yellow('Replacing wanglibao/settings.py STAGING')
                    run("fab config:'wanglibao/settings.py','STAGING \= False','STAGING \= True'")
                if env.mysql:
                    print red('Overwriting setting file to use local MYSQL')
                    run("fab config:'wanglibao/settings.py','LOCAL_MYSQL \= not PRODUCTION','LOCAL_MYSQL \= True'")

                print green('Collect static files')
                run("python manage.py collectstatic --noinput")

                print green('clean published files')
                run("rm publish/static/config.rb")
                run("rm -rf publish/static/sass")
                run("rm -rf publish/static/images/images-original")
                with cd('publish'):
                    run("find . | grep .coffee | xargs rm")

                print green("published files cleaned, copy it to /var/static/wanglibao")
                sudo('mkdir -p /var/static/wanglibao')
                sudo('cp -r publish/static/* /var/static/wanglibao/')
                sudo('rm -r publish')
                print green("static files copied and cleaned")

                print green("Generate media folder")
                create_folder('/var/media/wanglibao', owner='www-data', group='www-data', mod='775')

                print green("copy build to /var/wsgi/wanglibao/")

                print green("move the old deploy to back up folder")
                if exists('/var/wsgi/wanglibao-backup'):
                    sudo('rm -r /var/wsgi/wanglibao-backup')
                if exists('/var/wsgi/wanglibao'):
                    sudo('mv /var/wsgi/wanglibao /var/wsgi/wanglibao-backup')
                sudo('mkdir -p /var/wsgi/wanglibao')
                sudo('cp -r . /var/wsgi/wanglibao')
                sudo('chgrp -R www-data /var/wsgi/wanglibao')
                sudo('chown -R www-data /var/wsgi/wanglibao')

            with cd('/var/wsgi/wanglibao'):
                # use --noinput to prevent create super user. When super user created, then a profile object needs
                # to be created, at that point, that table is not created yet. Then it crashes.
                with hide('output'):
                    run("python manage.py syncdb --noinput")
                run("python manage.py migrate")

            print green("Copy apache config file")

            sudo('cp %s /etc/apache2/sites-available/' % env.apache_conf)
            # Disable all other sites
            sudo('rm -f /etc/apache2/sites-enabled/*')
            sudo('a2ensite %s' % os.path.split(env.apache_conf)[-1])

            sudo('service apache2 reload')


@roles('lb')
def config_loadbalancer():
    with cd(env.path):
        generate_nginx_conf()
        sudo('service nginx reload')


@task
def deploy():
    execute(init)

    execute(check_out)

    if env.roledefs['old_lb']:
        execute(take_out_of_rotation)

    execute(config_apache)
    execute(setup_cron_tab)

    # Now ready to update lb config
    if env.roledefs['lb']:
        execute(config_loadbalancer)

    if env.get('group') == 'staging':
        sudo('a2ensite chandao.conf')
        sudo('service apache2 reload')

    banner('Deploy Succeeded. Go Home!')


def banner(message):
    host_string = "%s (%s)" % (message, env.host_string)

    print green(reindent("""
    #########################################################################
    ## %s
    #########################################################################
    """ % host_string, 0))
