import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanglibao.settings')

from StringIO import StringIO
import logging
from file_storage.models import File
from file_storage.oss_util import oss_save


mark_file = '/tmp/migrate_mark'
error_file = '/tmp/migrate_error'
log_file = '/tmp/migrate_log'

logger = logging.getLogger('oss.migrate')
logger.addHandler(logging.FileHandler(log_file))
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

def get_mark():
    try:
        with open(mark_file) as f:
            return int(f.read())
    except:
        return 0

def save_mark(id_to_processed):
    with open(mark_file, 'w') as f:
        f.write(str(id_to_processed))

def save_error(id_error):
    with open(error_file, 'a') as f:
        f.write('%s\n'%id_error)

def process_file(file_id):
    mfile = File.objects.get(id=file_id)
    path = mfile.path
    file_to_write = StringIO()
    file_to_write.write(mfile.content)
    file_to_write.seek(0)
    saved_size  = oss_save(path, file_to_write)
    if saved_size != mfile.size:
        raise IOError('error save to oss %s, with saved file size %s'%(file_id, saved_size))
    return saved_size

def get_next_id(current_id, stop_mark=None):
    while True:
        if stop_mark and stop_mark == current_id:
            return
        mfile = File.objects.filter(id__gt=current_id).order_by('id').first()
        if mfile:
            current_id = mfile.id
            yield current_id
        else:
            return

def process_all(stop_mark=None):
    finished_id = get_mark()
    logger.info( 'start upload from %s'%(finished_id))
    for mid in get_next_id(finished_id, stop_mark=stop_mark):
        try:
            size = process_file(mid)
            save_mark(mid)
            logger.info('process %s, %s Byte uploaded'%(mid, size))
        except Exception,e:
            logger.exception(e)
            save_error(mid)

if __name__ == '__main__':
    # save_mark(1)
    # assert get_mark() == 1
    if len(sys.argv) > 1:
        ids = [int(file_id) for file_id in sys.argv[1:]]
        print 'process ids %s' % ids
        for id in ids:
            process_file(id)
        exit()
    process_all()
    # print File.objects.filter(id=2).first().id

