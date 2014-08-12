from contextlib import contextmanager
import os
from StringIO import StringIO
from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists, contains
from fabric_components.folder import create_folder
from fabric_components.apache import install_apache
from fabric_components.mysql import install_mysql, db_env, create_database, create_user, apt_get
from config.nginx_conf import generate_conf


def production():
    env.host_string = 'www.wanglibao.com'
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
    env.apache_conf = 'wanglibao.conf'


def pre_production():
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = False

    env.mysql = False  # Use RDS, so we no need to install mysql
    env.apache_conf = 'dev.conf'


def dev():
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'nginx'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = True

    env.mysql = True
    env.apache_conf = 'dev.conf'


def staging():
    env.user = 'deploy'
    env.password = 'wanglibank'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True
    env.staging = True

    env.mysql = True
    env.apache_conf = 'staging.conf'


if env.get('group') == 'staging':
    env.roledefs = {
        'lb': ['staging.wanglibao.com'],
        'web': ['staging.wanglibao.com'],
        'task_queue': ['staging.wanglibao.com'],
        'db': ['staging.wanglibao.com'],
    }
    staging()

elif env.get('group') == 'production':
    env.roledefs = {
        'lb': ['www.wanglibao.com'],
        'web': ['www.wanglibao.com'],
        'task_queue': ['www.wanglibao.com']
    }
    production()

elif env.get('group') == 'dev':
    env.roledefs = {
        'lb': ['192.168.1.162'],
        'web': ['192.168.1.184', '192.168.1.160'],
        'cron_tab': ['192.168.1.184'],
        'db': ['192.168.1.161'],
    }
    dev()


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


def init():
    """
    Setup the server for the first time
    :return:
    """

    create_folder(env.path, mod="777")
    create_folder('/var/run/wanglibao/', owner='www-data', group='www-data', mod='770')
    create_folder('/var/log/wanglibao/', owner='www-data', group='www-data', mod='770')

    apt_get('supervisor')
    apt_get("gcc", "python-setuptools", "python-all-dev", "libpq-dev", "libjpeg-dev")
    sudo("easy_install pip")
    new_virtualenv()

    if env.host_string in env.roledefs['web']:
        install_rabbit_mq()
        install_apache(mods=['ssl', 'headers', 'rewrite'], disable_sites=['default'])

        me = run('whoami')
        sudo('adduser %s www-data' % me)

        apt_get('libfreetype6-dev')

        apt_get("git")
        apt_get('libxml2-dev', 'libxslt1-dev')
        apt_get('swig')
        apt_get('libmysqlclient-dev')

        print green("Install apache2 and wsgi mod")

    if env.host_string in env.roledefs['db']:
        install_mysql(server=True, client=True)
        db_env(database='wanglibao', database_user='wanglibao', password='wanglibank', database_password='wanglibank')
        create_database()
        create_user()

    if env.host_string in env.roledefs['lb']:
        sudo("add-apt-repository ppa:nginx/stable")
        sudo("apt-get update")
        apt_get('nginx')


@task
@roles('lb')
def generate_nginx_conf():
    print green('Generate the nginx conf file')
    conf_content = generate_conf(apps=env.roledefs['web'])
    put(StringIO(conf_content), "/etc/nginx/sites-available/wanglibao-proxy.conf", use_sudo=True)
    with settings(warn_only=True):
        sudo('nginx_dissite default')
    sudo('nginx_ensite wanglibao-proxy.conf')


@task
@roles('lb', 'web', 'db')
def check_out():
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
                    else:
                        run('git checkout %s' % env.branch)
                        run('git pull')

                    run("git checkout %s" % env.branch)


@task
@roles('lb', 'web', 'db')
def deploy():
    with cd(env.path):
        sudo("cp %s/vender/nginx_util/* /usr/bin/" % env.depot_name)

        if env.host_string in env.roledefs['cron_tab']:
            print green('add crontab')
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

        if env.host_string in env.roledefs['web']:
            with virtualenv():
                with cd(os.path.join(env.path, env.depot_name)):
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
                    with hide('output'):
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

                    sudo('cp %s /etc/apache2/sites-available/' % env.apache_conf)
                    sudo('a2ensite %s' % env.apache_conf)

                    sudo('service apache2 reload')

        if env.host_string in env.roledefs['cron_tab']:
            print green('Start the supervisor in daemon mode')

            with cd('/var/wsgi/wanglibao'):
                if exists('/var/run/wanglibao/supervisor.pid'):
                    run("python manage.py supervisor stop all")
                    sudo("kill `cat /var/run/wanglibao/supervisor.pid`")
                run("python manage.py supervisor --daemonize --logfile=/var/log/wanglibao/supervisord.log --pidfile=/var/run/wanglibao/supervisor.pid")
                run("python manage.py supervisor update")
                run("python manage.py supervisor restart all")

        if env.host_string in env.roledefs['lb']:
            generate_nginx_conf()
            sudo('service nginx reload')
        print green("""
        #########################################################################
        ##         Deploy Succeeded. Go Home!           #########################
        #########################################################################
""")


def execute(command):
    with virtualenv():
        with cd('/var/wsgi/wanglibao'):
            run(command)
