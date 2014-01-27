from django.db import models


class Bank(models.Model):
    name = models.CharField(max_length=128)
    phone = models.CharField(max_length=32)
    description = models.TextField()
    home_url = models.URLField()

    def __unicode__(self):
        return u"%s" % (self.name, )


class BankFinancing(models.Model):
    name = models.CharField(max_length=128)
    product_code = models.CharField(max_length=128)
    bank = models.ForeignKey(Bank)
    period = models.FloatField(help_text="Count in month")
    max_expected_profit_rate = models.FloatField()
    risk_level = models.CharField(max_length=32)

    sale_start_date = models.DateField()
    sale_end_date = models.DateField()
    profit_start_date = models.DateField()
    profit_end_date = models.DateField()

    profit_type = models.CharField(max_length=32)

    currency = models.CharField(max_length=32)

    product_type = models.CharField(max_length=32, help_text=u"The type, structure, etc")
    principle_guaranteed = models.BooleanField(default=False)

    invest_threshold = models.FloatField(help_text="minimum investment in 10k")
    invest_step = models.FloatField()
    invest_method = models.TextField()

    face_value = models.FloatField()

    region = models.TextField()

    profit_target = models.CharField(max_length=32)
    profit_rate = models.FloatField()
    profit_calculation = models.TextField()

    invest_target = models.TextField()
    related_target = models.TextField()

    def __unicode__(self):
        return u"%s" % (self.name, )



