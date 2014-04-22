from django.core.management.base import BaseCommand
from trust.models import Trust
from wanglibao_bank_financing.models import BankFinancing
from wanglibao_cash.models import Cash
from wanglibao_fund.models import Fund
from wanglibao_robot.models import ScrawlItem


class Command(BaseCommand):

    def handle(self, *args, **options):
        items = (
            (Trust, 'trust'),
            (Fund, 'fund'),
            (BankFinancing, 'financing'),
            (Cash, 'cash'),
        )

        for model, type in items:
            for item in model.objects.all():
                s = ScrawlItem()
                s.type = type
                s.name = item.name
                if hasattr(item, 'issuer'):
                    s.issuer_name = item.issuer.name
                elif hasattr(item, 'bank'):
                    s.issuer_name = item.bank.name

                s.item_id = item.id
                s.save()

