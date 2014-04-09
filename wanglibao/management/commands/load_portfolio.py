from django.core.management.base import BaseCommand
from wanglibao_portfolio.mock_generator import MockGenerator


class Command(BaseCommand):

    def handle(self, *args, **options):
        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True
        MockGenerator.generate_products(clean)
        MockGenerator.load_portfolio_from_file('fixture/portfolio.csv', clean)