from contextlib import contextmanager
import os
from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists, contains
from fabric_components.folder import create_folder
from fabric_components.apache import install_apache
from fabric_components.mysql import install_mysql, db_env, create_database, create_user, apt_get


def prepare():
    local("python manage.py test wanglibao")
    local("git add -p && git commit")
    local("git push")


def testserver():
    env.host_string = '192.168.1.161'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'ssh://192.168.1.100/~/developer/django/wanglibao-back'
    env.depot_name = 'wanglibao'
    env.branch = "master"

    env.pip_install = "pip install --index-url http://pypi.douban.com/simple/ -r requirements.txt"
    env.pip_install_command = "pip install --index-url http://pypi.douban.com/simple/"

    env.debug = True
    env.production = False
    env.staging = False

    env.mysql = True


def production():
    env.host_string = '115.28.151.49'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'production2.0'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = False

    env.mysql = False  # Use RDS, so we no need to install mysql
    env.create_ssl_cert = False  # Production's key is maintained differently


def staging():
    env.host_string = 'staging.wanglibao.com'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'production2.0'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = True

    env.mysql = True
    env.create_ssl_cert = True


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


def publish():
    files = [
        'home0.jpg',
        'home1.jpg',
        'home2.jpg',
        'banner0.jpg',
        ]

    for file in files:
        local('osscmd.py put static/images/%s oss://wanglibao/images/%s' % (file, file))

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


def install_rabbit_mq():
    apt_get("software-properties-common")

    if not contains('/etc/apt/sources.list', 'rabbitmq'):
        sudo("add-apt-repository \"deb http://www.rabbitmq.com/debian/ testing main\"")
        run("wget http://www.rabbitmq.com/rabbitmq-signing-key-public.asc")
        sudo("apt-key add rabbitmq-signing-key-public.asc")
        sudo("apt-get update")

    apt_get("rabbitmq-server")


def deploy():
    path = env.path
    scrawl_job_file = '/usr/bin/scrawl_job'
    manage_py = '/var/wsgi/wanglibao/manage.py'
    log_file = '/var/log/wanglibao/scrawl.log'

    p2p_watchdog = '/usr/bin/p2p'
    p2p_log = '/var/log/wanglibao/p2p.log'

    sync_sm_info = '/usr/bin/sync_sm_info'
    sync_sm_income = '/usr/bin/sync_sm_income'
    sync_sm_log = '/var/log/wanglibao/sync_sm.log'

    print red("Begin deploy: ")
    create_folder(path, mod="777")

    print green("Create log folder")
    create_folder('/var/log/wanglibao/', owner='www-data', group='www-data', mod='770')
    # Add deploy account to www-data to inherit the permission on log folder, prevent permission issue
    sudo('adduser `whoami` www-data')

    with cd(path):
        print green("check out the build")

        print green("Install git")
        apt_get("git")

        print green("Install lxml dependency")
        apt_get('libxml2-dev', 'libxslt1-dev')

        print green("Install apache2 and wsgi mod")
        install_apache(mods=['ssl', 'headers', 'rewrite'], disable_sites=['default'])

        print green("Setup mysql")
        install_mysql(server=True, client=True)
        db_env(database='wanglibao', database_user='wanglibao', password='wanglibank', database_password='wanglibank')
        create_database()
        create_user()

        apt_get('libmysqlclient-dev')

        apt_get('libfreetype6-dev')

        print green('add crontab')
        sudo('echo "#!/bin/bash" > %s' % scrawl_job_file)
        sudo('echo %s &>> %s' % (env.activate, scrawl_job_file))
        sudo('echo "date > %s" >> %s' % (log_file, scrawl_job_file))
        sudo('echo "cd /var/wsgi/wanglibao/" >> %s' % scrawl_job_file)
        sudo('echo "python %s %s &>> %s">> %s' % (manage_py, 'run_robot', log_file, scrawl_job_file))
        sudo('echo "python %s %s &>> %s">> %s' % (manage_py, 'load_cash', log_file, scrawl_job_file))
        sudo('echo "python %s %s &>> %s">> %s' % (manage_py, 'scrawl_fund', log_file, scrawl_job_file))
        sudo('echo "date >> %s" >> %s' % (log_file, scrawl_job_file))
        sudo('chmod +x %s' % scrawl_job_file)
        sudo('echo "SHELL=/bin/bash" > /tmp/tmp_tab')
        sudo('echo "0 0 * * * %s" >> /tmp/tmp_tab' % scrawl_job_file)
        sudo('crontab /tmp/tmp_tab')

        add_cron_tab(p2p_watchdog, p2p_log, env, '*/10 * * * *', manage_py, ['p2p_watchdog'])
        add_cron_tab(sync_sm_info, sync_sm_log, env, '0 */1 * * *', manage_py, ['syncsm -f', 'syncsm -m'])
        add_cron_tab(sync_sm_income, sync_sm_log, env, '0 18-23/1 * * *', manage_py, ['syncsm -i'], _end=True)

        if not exists(os.path.join(path, env.depot_name)):
            print green('Git folder not there, create it')
            run("git clone %s" % env.depot)
            sudo("chmod 777 %s" % env.depot_name)
            with cd(env.depot_name):
                run("git checkout %s" % env.branch)
        else:
            print green('Found depot, pull changes')
            with cd(env.depot_name):
                run('git reset --hard HEAD')
                run('git remote set-url origin %s' % env.depot)
                run("git checkout %s" % env.branch)
                run("git pull")

        apt_get("gcc", "python-setuptools", "python-all-dev", "libpq-dev", "libjpeg-dev")
        print green("Install pip and virtualenv")
        sudo("easy_install pip")

        new_virtualenv()

        with virtualenv():
            with cd(os.path.join(path, env.depot_name)):
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
                    run("python manage.py syncdb --noinput")
                    run("python manage.py migrate")

                print green("Copy apache config file")
                if env.production and not env.staging:
                    sudo('cp wanglibao.conf /etc/apache2/sites-available')
                    sudo('a2ensite wanglibao.conf')
                if env.staging:
                    sudo('cp staging.conf /etc/apache2/sites-available')
                    sudo('a2ensite staging.conf')

                print green('apache server configured, restart it')
                sudo('service apache2 reload')
                print green('deploy finished')


def execute(command):
    with virtualenv():
        with cd('/var/wsgi/wanglibao'):
            run(command)
