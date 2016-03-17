from django.db.models import Q
from django.utils import timezone
from wanglibao_announcement.models import Announcement
from marketing.utils import utype_is_mobile


def get_announcement_list(request):
    is_mobile = utype_is_mobile(request)
    if is_mobile:
        device_type = 'mobile'
    else:
        device_type = 'pc'

    Homepage = Announcement.objects.filter(Q(starttime__lte=timezone.now(),
                                             endtime__gte=timezone.now(),
                                             status=1) &
                                           (Q(type='all') | Q(type='homepage') &
                                            (Q(device=device_type) |
                                             Q(device='pc&app')))).order_by('-priority', '-createtime')
    return Homepage


def AnnouncementHomepage(*args):
    Homepage = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='homepage')).filter(status=1).order_by('-priority', '-createtime')
    return Homepage


def AnnouncementP2P(*args):
    P2P = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='p2p')).filter(status=1, device='pc').order_by('-priority', '-createtime')[:1]
    return P2P


def AnnouncementP2PNew(*args):
    P2P = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(status=1, type='p2pnew', device='pc').order_by('-priority', '-createtime')[:1]
    return P2P


def AnnouncementTrust(*args):
    Trust = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='trust')).filter(status=1, device='pc').order_by('-priority', '-createtime')[:1]
    return Trust


def Announcementfund(*args):
    Fund = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='fund')).filter(status=1, device='pc').order_by('-priority', '-createtime')[:1]
    return Fund


def AnnouncementAccounts(*args):
    Accounts = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='accounts')).filter(status=1, device='pc').order_by('-priority', '-createtime')[:1]
    return Accounts