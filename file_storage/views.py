# coding=utf-8
from email.utils import formatdate
import mimetypes
from django.core.files.storage import default_storage
from django.http import Http404, HttpResponse
import time
from file_storage.models import File


def serve(request, path):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})
    """
    # file_record = File.objects.filter(path=path).first()

    if not default_storage.exists(path):
        raise Http404(u'页面不存在')

    #  TODO  if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
    #                             statobj.st_mtime, statobj.st_size):
    #        return HttpResponseNotModified()
    last_modified = formatdate(time.mktime(default_storage.modified_time(path).timetuple()))
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'

    file_data = default_storage.open(path).read()
    response = HttpResponse(file_data, content_type=content_type)

    response["Last-Modified"] = last_modified
    response["Content-Length"] = default_storage.size(path)

    if encoding:
        response["Content-Encoding"] = encoding
    print 'serving file %s %s' % (len(file_data), path)
    return response
