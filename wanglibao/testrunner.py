from django.test.runner import DiscoverRunner as TestRunner
import django

class DjangoTestSuiteRunner(TestRunner):
    # def run_tests(self, test_labels, extra_tests=None, **kwargs):
        # django.setup()

    def setup_databases(self, **kwargs):
        pass

    def teardown_databases(self, old_config, **kwargs):
        pass
