from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from wanglibao_fund.models import Fund


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete the duplicate fund items'),
    )

    def handle(self, *args, **options):
        dup_funds = [(f.id, f.product_code) for f in Fund.objects.all().order_by('product_code')]

        dup_funds_aggregated = {}
        for id, product_code in dup_funds:
            dup_funds_aggregated[product_code] = dup_funds_aggregated.get(product_code, []) + [id]

        ids_to_dedup = []
        for product_code, ids in dup_funds_aggregated.items():
            if len(ids) > 1:
                ids.sort()
                ids_to_dedup += ids[:-1]

        print '%d fund items to delete...' % len(ids_to_dedup)

        if len(ids_to_dedup) == 0:
            print 'No dup item found'
            return

        if options['delete']:
            Fund.objects.filter(id__in=ids_to_dedup).delete()
        else:
            # Show them
            print 'Ids: '
            print ','.join([str(id) for id in ids_to_dedup])

        print 'done'