from contextlib import contextmanager
import json
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
env.migrate = True
env.supervisord = True

env.apache_binding_interface = '*'
env.apache_binding_port = 80

# The env dict will be converted to a env.json and loaded in settings.py
env.env_dict = {}


def production():
    env.user = 'lishuo'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:wanglibao/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'production3.0'

    env.pip_install = "pip install -r requirements.txt"
    env.pip_install_command = "pip install"

    env.mysql = False  # Use RDS, so we no need to install mysql
    env.migrate = True
    env.supervisord = True

    env.environment = 'ENV_PRODUCTION'


def pre_production():
    env.user = 'lishuo'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:wanglibao/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'production3.0'

    env.pip_install = "pip install -r requirements.txt"
    env.pip_install_command = "pip install"

    env.mysql = False

    env.environment = 'ENV_PREPRODUCTION'


def dev():
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:wanglibao/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.mysql = True

    env.environment = 'ENV_STAGING'


def staging():
    env.user = 'deploy'
    env.password = 'wanglibank'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'git@github.com:wanglibao/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.mysql = True
    env.nginx_listen_on_80 = False

    env.environment = "ENV_STAGING"

    env.apache_binding_interface = '127.0.0.1'
    env.apache_binding_port = 8080


if env.get('group') == 'staging':
    env.roledefs = {
        'lb': ['staging.wanglibao.com'],
        'web': ['staging.wanglibao.com'],
        'web_private': ['127.0.0.1'],

        # task_queue should be ip
        'task_queue': ['staging.wanglibao.com'],
        # 'task_queue': ['111.206.165.43'],
        'task_queue_private': ['127.0.0.1'],

        'db': ['staging.wanglibao.com'],
        'old_lb': [],
        'old_web': [],
        'cron_tab': ['staging.wanglibao.com'],
    }
    staging()

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
            '192.168.1.43',
            '192.168.1.176'
        ],

        # Cron tab is the server with crontab running. NOTE: The crontab should be with new version, and only
        # one crontab server should be running at the same time.
        'cron_tab': ['192.168.1.43'],

        # DB is the db servers
        'db': [
            #'192.168.1.161'
        ],

        # Task queue server is the server running rabbitmq or redis.
        'task_queue': ['192.168.1.43'],
        'task_queue_private': ['127.0.0.1']
    }
    dev()

elif env.get('group') == 'production':
    env.roledefs = {
        'old_lb': [],
        'lb': ['115.28.151.49'],
        'old_web': [
            '115.28.166.203',
            '121.42.11.194'
        ],
        'old_web_private':[
            '10.144.172.198',
            '10.165.54.41'
        ],
        'web': [
            '115.28.166.203',
            '114.215.146.91'
        ],
        'web_private': [
            '10.144.172.198',
            '10.164.13.228'
        ],
        'cron_tab': ['114.215.146.91'],
        'db': [],
        'task_queue': ['114.215.146.91'],
        'task_queue_private': ['10.164.13.228'],

        'huifu_sign_server': ['115.28.151.49']
    }
    production()


elif env.get('group') == 'pre':
    env.roledefs = {
        # Old lb is the load balancer which points to old version, it should take out of the new webs
        'old_lb': [],

        # New lb is the load balancer which points to new version, it should only with new web
        'lb': ['115.28.80.27'],

        # Old web is the server running with old version, they should not be touched
        'old_web': [],

        # Web is the server to be deployed with new version
        'web': [
            '115.28.166.203',
            '121.42.11.194'
        ],
        'web_private': [
            '10.144.172.198',
            '10.165.54.41'
        ],

        # Cron tab is the server with crontab running. NOTE: The crontab should be with new version, and only
        # one crontab server should be running at the same time.
        'cron_tab': ['115.28.166.203'],

        # DB is the db servers
        'db': [
            # '115.28.240.194'
        ],

        # Task queue server is the server running rabbitmq or redis.
        'task_queue': ['115.28.166.203'],
        'task_queue_private': ['10.144.172.198'],

        'huifu_sign_server': ['115.28.151.49'],
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
        # sudo("apt-get update")

    apt_get("rabbitmq-server")


@task
@roles('lb', 'db', 'web')
def init():
    """
    Setup the server for the first time
    :return:
    """
    if env.get('no-init'):
        banner("SKIPPED INIT due to configuration")
        return

    banner("init")
    with hide("output"):
        # if not env.get('no-apt-update'):
        #     sudo('apt-get update')

        create_folder(env.path, mod="777")
        create_folder('/var/run/wanglibao/', owner='www-data', group='www-data', mod='770')
        create_folder('/var/log/wanglibao/', owner='www-data', group='www-data', mod='770')

        run('mkdir -p ~/.ssh && chmod 700 ~/.ssh')
        put('certificate/deployment', '~/.ssh/id_rsa')
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
                # sudo("apt-get update")
            apt_get('nginx')
            put("vender/nginx_util/*",  "/usr/bin/", use_sudo=True, mode="770")

        if env.host_string in env.roledefs['task_queue']:
            install_rabbit_mq()
            sudo('iptables -A INPUT -p tcp -m tcp --dport 5672 --tcp-flags SYN,RST,ACK,ACK SYN -j ACCEPT')
            users = sudo('rabbitmqctl list_users')
            if users.find('wanglibao') == -1:
                sudo('rabbitmqctl add_user wanglibao wanglibank')

            vhosts = sudo('rabbitmqctl list_vhosts')
            if vhosts.find('wanglibao') == -1:
                sudo('rabbitmqctl add_vhost wanglibao')
                sudo('rabbitmqctl set_permissions -p wanglibao wanglibao ".*" ".*" ".*"')


@task
@roles('lb')
def generate_nginx_conf():
    print green('Generate the nginx conf file for new lb')
    apps = env.roledefs['web']
    if 'web_private' in env.roledefs:
        apps = env.roledefs['web_private']

    conf_content = generate_conf(apps=apps,
                                 upstream_port=str(env.apache_binding_port),
                                 listen_on_80=env.nginx_listen_on_80)
    put(StringIO(conf_content), "/etc/nginx/sites-available/wanglibao-proxy.conf", use_sudo=True)
    #sudo('rm -f /etc/nginx/sites-enabled/*')
    sudo('rm -f /etc/nginx/sites-enabled/wanglibao-proxy.conf')
    sudo('nginx_ensite wanglibao-proxy.conf')


@task
@roles('old_lb')
def take_out_of_rotation():
    banner('Generate the nginx conf file for old lb')
    apps = env.roledefs['old_web']
    if 'old_web_private' in env.roledefs:
        apps = env.roledefs['old_web_private']
    conf_content = generate_conf(apps=apps)
    put(StringIO(conf_content), "/etc/nginx/sites-available/wanglibao-proxy.conf", use_sudo=True)
    with settings(warn_only=True):
        sudo('nginx_dissite default')
    sudo('nginx_ensite wanglibao-proxy.conf')


@task
@roles('lb', 'web', 'db')
def check_out():
    banner("check out")
    if not env.get('no-checkout'):
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
                        run('git clean -f -d')
                        run('git remote set-url origin %s' % env.depot)

                        result = run('git show-ref --verify --quiet refs/heads/%s' % env.branch)
                        if result.return_code > 0:
                            run('git fetch origin %s:%s' % (env.branch, env.branch))
                            run("git checkout %s" % env.branch)
                        else:
                            run('git checkout %s' % env.branch)
                            run('git pull origin %s' % env.branch)


@task
@roles('cron_tab')
def setup_cron_tab():
    banner("Setup crontab")
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

        if env.supervisord:
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

                print yellow('Replacing wanglibao/settings.py ENV')
                run("fab config:'wanglibao/settings.py','ENV \= ENV_DEV','ENV \= %s'" % env.environment)

                print yellow('Generating env.json from env.env_dict')
                task_queue_host = env.roledefs['task_queue'][0]
                if 'task_queue_private' in env.roledefs:
                    task_queue_host = env.roledefs['task_queue_private'][0]

                env.env_dict["BROKER_URL"] = "amqp://wanglibao:wanglibank@%(task_queue_host)s/wanglibao" % {
                    'task_queue_host': task_queue_host
                }

                json_env = json.dumps(env.env_dict)
                put(StringIO(json_env), 'env.json')

                print green('Collect static files')
                run("python manage.py collectstatic --noinput")

                print green('clean published files')
                run("rm publish/static/config.rb")
                run("rm -rf publish/static/sass")
                run("rm -rf publish/static/images/images-original")
                with cd('publish'):
                    run("find . | grep .coffee | xargs rm -rf")

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

            if env.migrate:
                with cd('/var/wsgi/wanglibao'):
                    # use --noinput to prevent create super user. When super user created, then a profile object needs
                    # to be created, at that point, that table is not created yet. Then it crashes.
                    with hide('output'):
                        run("python manage.py syncdb --noinput")
                    run("python manage.py migrate")

            with open(env.apache_conf, 'r') as apache_config_file:
                content = apache_config_file.read()
                result = content % {
                    'apache_binding_interface': env.apache_binding_interface,
                    'apache_binding_port': env.apache_binding_port
                }
                put(StringIO(result), '/etc/apache2/sites-available/%s' % os.path.split(env.apache_conf)[-1], use_sudo=True)

            # Disable all other sites
            sudo('rm -f /etc/apache2/sites-enabled/*')
            sudo('a2ensite %s' % os.path.split(env.apache_conf)[-1])

            if env.get('group') == 'staging':
                sudo('a2ensite chandao.conf')
                sudo('ln -s /etc/apache2/sites-available/staging_80_redirect /etc/apache2/sites-enabled/')

            sudo('service apache2 reload')
            sudo('chown -R www-data:www-data /var/log/wanglibao/')


@task
@roles('lb')
def config_loadbalancer():
    with cd(env.path):
        generate_nginx_conf()
        sudo('service nginx reload')
        sudo('rm -rf /var/cache/nginx')

@task
def deploy():
    if env.get("fast", "").lower() == "true":
        execute(check_out)
        execute(config_apache)
        banner('Fast Deploy Succeeded')
        return

    execute(init)

    execute(check_out)

    if env.roledefs['old_lb']:
        execute(take_out_of_rotation)

    execute(config_apache)
    execute(setup_cron_tab)

    # Now ready to update lb config
    if env.roledefs['lb']:
        execute(config_loadbalancer)

    banner('Deploy Succeeded. Go Home!')


def banner(message):
    host_string = "%s (%s)" % (message, env.host_string)

    print green(reindent("""
    #########################################################################
    ## %s
    #########################################################################
    """ % host_string, 0))
