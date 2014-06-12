
class Pay:
    def __init__(self):
        pass

    def sign_data(self, raw_data):
        raise NotImplementedError

    def verify_sign(self, raw_data, sign):
        raise  NotImplementedError

    def pay(self):
        raise  NotImplementedError