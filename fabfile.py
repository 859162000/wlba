from contextlib import contextmanager
import os
from fabric.api import *
from fabric.colors import green, red
from fabric.contrib.files import exists
from fabric.contrib import django


def prepare():
    local("python manage.py test wanglibao")
    local("git add -p && git commit")
    local("git push")


def testserver():
    env.host_string = '192.168.56.199'
    env.path = '/home/lishuo/wanglibao'
    env.activate = 'source /home/lishuo/wanglibao/virt-python/bin/activate'
    env.depot = 'ssh://lishuo@192.168.56.1/~lishuo/developer/django/wanglibao/wanglibao'
    env.depot_name = 'wanglibao'

    env.pip_install = "pip install --index-url http://pypi.hustunique.com/simple/ -r requirements.txt"

def production():
    env.host_string = 'o-value.com'
    env.path = '/home/lishuo/wanglibao'
    env.activate = 'source /home/lishuo/wanglibao/virt-python/bin/activate'
    env.depot = 'https://github.com/shuoli84/wanglibao-backend.git'
    env.depot_name = 'wanglibao-backend'

    env.pip_install = "pip install -r requirements.txt"

def new_virtualenv():
    with cd(env.path):
        sudo("apt-get -q -y install gcc python-setuptools python-all-dev libpq-dev libjpeg-dev")
        sudo("easy_install pip virtualenv")
        # TODO find a better path for virt env
        run("virtualenv virt-python")

@contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield


def deploy():
    path = '/home/lishuo/wanglibao'

    print red("Begin deploy: ")
    # todo if the folder not existed, create it
    run('mkdir -p %s' % path)
    with cd(path):
        run("pwd")

        print green("check out the build")

        if not exists(os.path.join(path, env.depot_name)):
            print green('Git folder not there, clone it from local depot')
            # TODO get the local git path instead of hard code
            run("git clone %s" % env.depot)
        else:
            print green('Found depot, pull changes')
            with cd(env.depot_name):
                run("git pull %s" % env.depot)

        print green("Refresh apt")
        sudo("apt-get update")

        print green("Install pip and virtualenv")
        new_virtualenv()
        with virtualenv():
            with cd(os.path.join(path, env.depot_name)):
                run("pip install --index-url http://pypi.hustunique.com/simple/ -r requirements.txt")

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
                # TODO set permission
                print green("static files copied and cleaned")

                print green("copy scripts to /var/wsgi/wanglibao/")
                sudo('mkdir -p /var/wsgi/wanglibao')
                sudo('cp -r . /var/wsgi/wanglibao')
                sudo('chgrp -R webuser /var/wsgi/wanglibao')
                sudo('chown -R www-data /var/wsgi/wanglibao')

                with cd('/var/wsgi/wanglibao'):
                    run("python manage.py syncdb")
                    run("python manage.py migrate")

                print green("Grant write permission on /tmp/ db file")
                sudo('chmod 777 /tmp/db.sqlite3')

                print green("Copy apache config file")
                sudo('cp wanglibao.conf /etc/apache2/sites-available')
                sudo('a2ensite wanglibao.conf')

                print green('apache server configured, restart it')
                sudo('service apache2 reload')
                print green('deploy finished')


def mock():
    with virtualenv():
        django.project('wanglibao')
        from trust.mock_generator import MockGenerator as TrustMockGenerator

        TrustMockGenerator.generate_issuer(clean=True)
        TrustMockGenerator.generate_trust(clean=True)


def mock_deployed():
    with virtualenv():
        with cd('/var/wsgi/wanglibao'):
            sudo('fab mock')
