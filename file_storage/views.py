# coding=utf-8
from email.utils import formatdate
import mimetypes
from django.http import Http404, CompatibleStreamingHttpResponse
import time
from file_storage.models import File


def serve(request, path):
    """
    Serve static files below a given point in the directory structure.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root' : '/path/to/my/files/'})
    """
    file_record = File.objects.filter(path=path).first()

    if not file_record:
        raise Http404(u'页面不存在')

    #  TODO  if not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'),
    #                             statobj.st_mtime, statobj.st_size):
    #        return HttpResponseNotModified()
    last_modified = formatdate(time.mktime(file_record.updated_at.timetuple()))
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'

    response = CompatibleStreamingHttpResponse(file_record.content, content_type=content_type)

    response["Last-Modified"] = last_modified
    response["Content-Length"] = file_record.size

    if encoding:
        response["Content-Encoding"] = encoding
    return response
