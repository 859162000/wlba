from contextlib import contextmanager
import os
from fabric.api import *
from fabric.colors import green, red
from fabric.contrib.files import exists


def prepare():
    local("python manage.py test wanglibao")
    local("git add -p && git commit")
    local("git push")


def testserver():
    env.host_string = '192.168.56.199'
    env.path = '/home/lishuo/wanglibao'
    env.activate = 'source /home/lishuo/wanglibao/virt-python/bin/activate'


def new_virtualenv():
    with cd(env.path):
        sudo("apt-get -q -y install gcc python-setuptools python-all-dev libpq-dev libjpeg-dev")
        sudo("easy_install pip virtualenv")
        run("virtualenv virt-python")

@contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield


def test():
    path = '/home/lishuo/wanglibao'

    print red("Begin deploy: ")
    # todo if the folder not existed, create it
    run('mkdir -p %s' % path)
    with cd(path):
        run("pwd")

        print green("check out the build")

        if not exists(os.path.join(path, 'wanglibao')):
            print green('Git folder not there, clone it from local depot')
            # TODO get the local git path instead of hard code
            run("git clone ssh://lishuo@192.168.56.1/~lishuo/developer/django/wanglibao/wanglibao")
        else:
            print green('Found depot, pull changes')
            run("git pull ssh://lishuo@192.168.56.1/~lishuo/developer/django/wanglibao/wanglibao")

        print green("Install pip and virtualenv")
        new_virtualenv()
        with virtualenv():
            with cd(os.path.join(path, 'wanglibao')):
                run("pip install --index-url http://pypi.hustunique.com/simple/ -r requirements.txt")

                print green('Collect static files')
                run("python manage.py collectstatic")

                print green('clean published files')
                run("rm publish/static/config.rb")
                run("rm -rf publish/static/sass")
                run("rm -rf publish/static/images/images-original")

                print green("published files cleaned, copy it to /var/static/wanglibao")
                sudo('mkdir -p /var/static/wanglibao')
                sudo('cp -r publish/static/* /var/static/wanglibao/')
                print green("static files copied")

                print green("Copy apache config file")
                sudo('cp wanglibao.conf /etc/apache2/sites-available')
                sudo('a2ensite wanglibao')

                print green('apache server configured, restart it')
                sudo('apache2ctl restart')
                print green('deploy finished')

