from StringIO import StringIO
from file_storage.models import File
from file_storage.oss_util import oss_save

mark_file = 'migrate_mark'
error_file = 'migrate_error'

def get_mark():
    try:
        with open(mark_file) as f:
            return int(f.read())
    except:
        return 0

def save_mark(id_to_processed):
    with open(mark_file, 'w') as f:
        f.write(id_to_processed)

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
        raise IOError('error save to oss %s'%file_id)
    return saved_size

def get_next_id(current_id):
    return File.objects.filter(id__gte=current_id).order_by('id').first()

def process_all():
    mid = get_mark()
    mid = get_next_id(mid)
    print 'start upload from %s'%(mid)
    while mid:
        try:
            size = process_file(mid)
            print 'process %s, %s Byte uploaded'%(mid, size)
            get_next_id(mid)
        except:
            save_error(mid)








if __name__ == '__init__':
    # save_mark(1)
    # assert get_mark() == 1
    print process_file(7193)

