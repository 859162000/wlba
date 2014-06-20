class P2PTrader(object):

    def __init__(self, product, user, request=None):
        self.user = user
        self.product = product
        self.request = request

    def purchase(self, amount):
        pass

    def __update_equity(self, amount):
        pass
