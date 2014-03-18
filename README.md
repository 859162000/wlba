wanglibao-backend
=================

The backend of wanglibao website

pip install virtualenv --index-url http://pypi.tuna.tsinghua.edu.cn/simple 
virtualenv env
source ../env/bin/activate
pip install -r requirements.txt --index-url http://pypi.tuna.tsinghua.edu.cn/simple

python manage.py syncdb
python manage.py generate_mock clean

bundle install
