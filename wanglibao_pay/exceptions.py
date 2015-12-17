# encoding=utf-8


class ThirdPayError(Exception):
    def __init__(self, code, message):
        super(ThirdPayError, self).__init__()
        self.code = code
        self.message = message

    def __str__(self):
        return "Error during request third pay:%s %s" % (self.code, self.message)

class VerifyError(Exception):
    def __init__(self, pem_path, content, signature):
        super(VerifyError, self).__init__()
        self.pem_path = pem_path
        self.content = content
        self.signature = signature

    def __str__(self):
        return "Signature verify error: using certificate %s for content %s with signature %s" % (
            self.pem_path, self.content, self.signature
        )


class CardException(Exception):
    pass


class ManyCardException(CardException):
    message = u"银行卡数量重复"


class AbnormalCardException(CardException):
    message = u"银行卡异常"
