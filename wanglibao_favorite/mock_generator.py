import random
from django.contrib.auth import get_user_model
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_favorite.models import FavoriteTrust, FavoriteFund, FavoriteFinancing
from wanglibao_fund.models import Fund


class MockGenerator(object):
    @classmethod
    def _generate_fav_by_model(cls, item_model, fav_model, count, clean=False):
        if clean:
            fav_model.objects.all().delete()

        items = item_model.objects.all()
        items_count = len(items)

        user = get_user_model().objects.all()[0]

        for i in range(0, count):
            fav_item = fav_model()
            fav_item.user = user
            fav_item.item = items[random.randrange(0, items_count)]
            fav_item.save()

    @classmethod
    def generate_fav_trusts(cls, clean=False):
        cls._generate_fav_by_model(Trust, FavoriteTrust, 100, clean=clean)

    @classmethod
    def generate_fav_funds(cls, clean=False):
        cls._generate_fav_by_model(Fund, FavoriteFund, 100, clean=clean)

    @classmethod
    def generate_fav_financings(cls, clean=False):
        cls._generate_fav_by_model(BankFinancing, FavoriteFinancing, 100, clean=clean)
