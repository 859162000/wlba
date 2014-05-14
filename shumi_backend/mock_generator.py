import random, datetime
from wanglibao_buy.models import FundHoldInfo, BindBank


# todo close mock generator
class MockGenerator(object):

    @classmethod
    def generate_fund_hold_info(cls, clean=False):
        if clean:
            [item.delete() for item in FundHoldInfo.objects.iterator()]
