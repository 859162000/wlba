#encoding=utf8
from Crypto.Cipher import AES
from wanglibao.settings import  AMORIZATION_AES_IV

class Crypt_Aes():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC
        self.IV = AMORIZATION_AES_IV
        self.padding = '\0'

    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.IV)
        x = len(text) % 16
        if x > 0:
            text += (16 - x) * self.padding
        self.ciphertext = cryptor.encrypt(text)
        return self.ciphertext

    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.IV)
        plain_text = cryptor.decrypt(text)
        return plain_text.rstrip(self.padding)

if __name__ == '__main__':
    key = '1234567890abcdef'
    data = '{"a": "123中文", sss} '
    ec = Crypt_Aes(key)
    encrpt_data = ec.encrypt(data)
    decrpt_data = ec.decrypt(encrpt_data)
    print encrpt_data
    print  decrpt_data
    print  decrpt_data == data

