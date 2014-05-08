wanglibao-backend
=================

The backend of wanglibao website

Create virtualenv
-----------------
- pip install virtualenv --index-url http://pypi.tuna.tsinghua.edu.cn/simple 
- virtualenv env

Install python packages
-----------------
- source ../env/bin/activate
- pip install -r requirements.txt --index-url http://pypi.tuna.tsinghua.edu.cn/simple

Create db
-----------------
- python manage.py syncdb
- python manage.py migrate
- python manage.py generate_mock clean

Install compass
-----------------
- gem install bundle
- bundle install

Languages or skills required
-----------------
Programming language: Python, Sass + Compass, jade (pyjade)
