from django.db.models import Q
from django.utils import timezone
from wanglibao_announcement.models import Announcement


def AnnouncementHomepage(*args):
    Homepage = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='homepage')).filter(status=1).order_by('-priority', '-updatetime')
    return Homepage


def AnnouncementP2P(*args):
    P2P = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='p2p')).order_by('-priority', '-updatetime')[:1]
    return P2P


def AnnouncementP2PNew(*args):
    P2P = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(status=1, type='p2pnew').order_by('-priority', '-updatetime')[:1]
    return P2P


def AnnouncementTrust(*args):
    Trust = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='trust')).filter(status=1).order_by('-priority', '-updatetime')[:1]
    return Trust


def Announcementfund(*args):
    Fund = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='fund')).filter(status=1).order_by('-priority', '-updatetime')[:1]
    return Fund


def AnnouncementAccounts(*args):
    Accounts = Announcement.objects.filter(starttime__lte=timezone.now(), endtime__gte=timezone.now())\
        .filter(Q(type='all') | Q(type='accounts')).filter(status=1).order_by('-priority', '-updatetime')[:1]
    return Accounts