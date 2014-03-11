from django.contrib.auth import get_user_model
from django.db import models
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_fund.models import Fund


class FavoriteTrust(models.Model):
    """
    The favorite trust relation defines user's collection on trust
    """
    user = models.ForeignKey(get_user_model())
    item = models.ForeignKey(Trust)


class FavoriteFinancing(models.Model):
    """
    The favorite financing relation defines user's collection on financing
    """
    user = models.ForeignKey(get_user_model())
    item = models.ForeignKey(BankFinancing)


class FavoriteFund(models.Model):
    """
    The favorite fund relation defines user's collection of fund
    """
    user = models.ForeignKey(get_user_model())
    item = models.ForeignKey(Fund)


