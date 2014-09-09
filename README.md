wanglibao-backend
=================

The backend of wanglibao website

Create virtualenv
-----------------
    $ pip install virtualenv --index-url http://pypi.tuna.tsinghua.edu.cn/simple 
    $ virtualenv env

Install python packages
-----------------
    $ source ../env/bin/activate
    $ pip install -r requirements.txt --index-url http://pypi.tuna.tsinghua.edu.cn/simple

Create db
-----------------
create database on UTF8 
    
    mysql> CREATE DATABASE wanglibao DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;

create database user
    
    mysql> INSERT INTO mysql.user(Host,User,Password) values("localhost","wanglibao",password("wanglibank"));

add Permissions

    mysql> grant all privileges on wanglibao.* to wanglibao@localhost identified by 'wanglibank';

flush system permissions 
    
    mysql>flush privileges;


Sync db
-----------------
    $ python manage.py syncdb
    $ python manage.py migrate
    $ python manage.py generate_mock clean

Install compass & sass
-----------------
do

    $ gem install bundle
    $ bundle install

or

    $ gem source --remove 'http://rubygems.org'
    $ gem source -a 'https://ruby.taobao.org'
    $ gem install compass --version=0.12.3
    $ gem install sass --version=3.2.14
    $ gem install susy --version=1.0.5
    $ gem install font-icons --pre



Languages or skills required
----------------------------
Programming language: `Python`, `Sass + Compass`, `jade (pyjade)`


Deploy
-----------------
    $ dev: fab deploy --set group=dev
    $ staging: fab deploy --set group=staging
    $ pre: fab deploy --set group=pre
    $ production: fab deploy --set group=production

Query example
-------------------
log in to web server through ssh, then run

    source /var/deploy/wanglibao/virt-python/bin/activate
    cd /var/wsgi/wanglibao/
    python manage.py shell

1. Get all equity and user's introduced by

    [(e.user.wanglibaouserprofile.phone, e.equity, "".join([str(hasattr(i.introduced_by, "wanglibaouserprofile") and i.introduced_by.wanglibaouserprofile.phone) + " " + i.introduced_by.username for i in e.user.introducedby_set.all()])) for e in p.equities.all()]


New Contract Template
------------------

    1. Create a jade under wanglibao_p2p/templates/xxx.jade
    2. in shell: pyjade wanglibao_p2p/templates/xxx.jade 
    3. Copy the generated html
    4. Open /admin, under p2p contract, create a new contract, give it a name and paste the generated html into content

