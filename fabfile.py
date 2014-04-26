from contextlib import contextmanager
import os
from fabric.api import *
from fabric.colors import green, red, yellow
from fabric.contrib.files import exists
from fabric.contrib import django


def prepare():
    local("python manage.py test wanglibao")
    local("git add -p && git commit")
    local("git push")


def testserver():
    env.host_string = '192.168.56.199'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'ssh://192.168.56.1/~/developer/django/wanglibao/wanglibao'
    env.depot_name = 'wanglibao'
    env.branch = "master"

    env.pip_install = "pip install --index-url http://pypi.douban.com/simple/ -r requirements.txt"
    env.pip_install_command = "pip install --index-url http://pypi.douban.com/simple/"

    env.debug = True
    env.production = False
    env.mysql = True


def production():
    env.host_string = '115.28.151.49'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'master'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True

    env.mysql = False  # Use RDS, so we no need to install mysql


def staging():
    env.host_string = '192.168.1.12'
    env.path = '/var/deploy/wanglibao'
    env.activate = 'source ' + env.path + '/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'
    env.branch = 'logging'

    env.pip_install = "pip install -r requirements.txt -i http://pypi.douban.com/simple/"
    env.pip_install_command = "pip install -i http://pypi.douban.com/simple/"

    env.debug = False
    env.production = True

    env.mysql = True


def new_virtualenv():
    with cd(env.path):
        sudo("apt-get -q -y install gcc python-setuptools python-all-dev libpq-dev libjpeg-dev")
        sudo("easy_install pip")
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


def deploy():
    path = env.path
    scrawl_job_file = '/usr/bin/scrawl_job'
    manage_py = os.path.join(env.path, env.depot_name, 'manage.py')
    log_file = '/var/log/wanglibao/scrawl.log'

    print red("Begin deploy: ")
    sudo('touch log_file')
    sudo('mkdir -p %s' % path)
    sudo('mkdir -p /var/log/wanglibao/')
    sudo('chown -R www-data /var/log/wanglibao')
    sudo('chgrp -R www-data /var/log/wanglibao')
    sudo('chmod -R 770 /var/log/wanglibao')
    with cd(path):

        print green("check out the build")

        print green("Install git")
        sudo("apt-get install git")

        print green("Install lxml dependency")
        sudo("apt-get -q -y install libxml2-dev libxslt1-dev")

        print green("Install apache2 and wsgi mod")
        sudo("apt-get -q -y install apache2 python-setuptools libapache2-mod-wsgi")
        sudo("a2dissite default")

        print green("Setup mysql")
        if env.mysql:
            print yellow("Install mysql server")
            sudo("apt-get -q -y install mysql-server ")

        print green("Install mysql client")
        sudo("apt-get -q -y install mysql-client")
        # TODO setup database

        print green('add crontab')
        sudo('echo "date > %s" > %s' % (log_file, scrawl_job_file))
        sudo('echo %s >> %s' % (env.activate, scrawl_job_file))
        sudo('echo "python %s %s >> %s">> %s' % (manage_py, 'run_robot', log_file, scrawl_job_file))
        sudo('echo "python %s %s >> %s">> %s' % (manage_py, 'load_cash', log_file, scrawl_job_file))
        sudo('echo "python %s %s >> %s">> %s' % (manage_py, 'scrawl_fund', log_file, scrawl_job_file))
        sudo('echo "date >> %s" >> %s' % (log_file, scrawl_job_file))
        sudo('chmod +x %s' % scrawl_job_file)
        sudo('echo "0 0 * * * %s" > /tmp/scrawl_tab' % scrawl_job_file)
        sudo('crontab /tmp/scrawl_tab')

        if not exists(os.path.join(path, env.depot_name)):
            print green('Git folder not there, create it')
            sudo("chmod 777 %s" % path)
            run("git clone %s" % env.depot)
            sudo("chmod 777 %s" % env.depot_name)
            with cd(env.depot_name):
                run("git checkout %s" % env.branch)
        else:
            print green('Found depot, pull changes')
            with cd(env.depot_name):
                run('git reset --hard HEAD')
                run("git pull")
                run("git checkout %s" % env.branch)

        print green("Refresh apt")
        sudo("apt-get update")
        sudo("apt-get install libmysqlclient-dev")

        print green("Install pip and virtualenv")
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

                print green("Generate media folder")
                sudo('mkdir -p /var/media/wanglibao')
                sudo('chmod -R 775 /var/media/wanglibao')
                print green("static files copied and cleaned")

                print green("copy scripts to /var/wsgi/wanglibao/")

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
                    run("python manage.py syncdb")
                    run("python manage.py migrate")

                print green("Copy apache config file")
                sudo('cp wanglibao.conf /etc/apache2/sites-available')
                sudo('a2ensite wanglibao.conf')

                print green('apache server configured, restart it')
                sudo('service apache2 reload')
                print green('deploy finished')
