from django.core.management.base import BaseCommand, CommandError
from wanglibao.mock_generator import MockGenerator

class Command(BaseCommand):

    def handle(self, *args, **options):
        clean = False
        if len(args) >= 1 and args[0] == "clean":
            clean = True
        MockGenerator.generate(clean)