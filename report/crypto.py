import base64
import os
from Crypto.Cipher import AES
from M2Crypto import RSA,BIO,EVP
import binascii
from wanglibao import settings

class Rsa(object):

    @classmethod
    def gen_rsa_key_pair(cls, rsalen=1024):
        rsa_key = RSA.gen_key(rsalen, 3, lambda *args: None)
        rsa_key.save_key("pri_key.pem", None)
        rsa_key.save_pub_key("pub_key.pem")

    @classmethod
    def encrypt(cls, data):
        #pub_key_file = os.path.join(settings.BASE_DIR, "pub_key.pem")
        pub_key_file = os.path.join(settings.CERT_DIR, "pub_key.pem")
        pub_key = RSA.load_pub_key(pub_key_file)

        print

        return pub_key.public_encrypt(data, RSA.pkcs1_oaep_padding)

    @classmethod
    def decrypt(cls, data):
        #string = open("pri_key.pem", "rb").read()
        string = open(settings.CERT_DIR + "pri_key.pem", "rb").read()
        bio = BIO.MemoryBuffer(string)
        pri_key = RSA.load_key_bio(bio)
        return pri_key.private_decrypt(data, RSA.pkcs1_oaep_padding)


class Aes(object):

    @classmethod
    def encrypt(cls, key, plain_text):
        iv = '\0' * 16
        cryptor = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
        padding = '\0'
        length = 16
        count = plain_text.count('')
        if count < length:
            add = (length - count) + 1
            plain_text += (padding * add)
        elif count > length:
            add = (length - (count % length)) + 1
            plain_text += (padding * add)
        cipher_text = cryptor.encrypt(plain_text)
        return base64.b64encode(cipher_text)

    @classmethod
    def decrypt(cls, key, text):
        iv = '\0' * 16
        cryptor = AES.new(key=key, mode=AES.MODE_CBC, IV=iv)
        text = base64.b64decode(text)
        plain_text = cryptor.decrypt(text)
        return plain_text.rstrip("\0")


class ReportCrypto(object):
    @classmethod
    def encrypt_file(cls, content):
        rsa = Rsa()
        ase = Aes()
        crypt_key = binascii.b2a_hex(os.urandom(16))
        encrypt_text = ase.encrypt(crypt_key, content)
        encrypt_key = base64.b64encode(rsa.encrypt(crypt_key))
        return "%s\n%s" % (encrypt_key, encrypt_text)

    @classmethod
    def decrypt_file(cls, path):
        file_object = open(path, 'r')
        rsa = Rsa()
        ase = Aes()
        all_line = file_object.readlines()
        all_key = base64.decodestring(all_line[0].strip('\n'))
        all_text = all_line[1].strip('\n')
        print(all_text)
        decrypt_key = rsa.decrypt(all_key)
        print(decrypt_key)
        decrypt_text = ase.decrypt(decrypt_key, all_text)
        print(decrypt_text)
