from cryptography.fernet import Fernet
from .key import key

# 키 생성
# key = Fernet.generate_key()
key = key()
cipher_suite = Fernet(key)

def encrypt_file(file):
    # 파일 내용을 읽고 암호화합니다.
    encrypted_file = cipher_suite.encrypt(file)
    return encrypted_file

def decrypt_file(file):
    # 파일 내용을 읽고 복호화합니다.
    decrypted_file = cipher_suite.decrypt(file)
    return decrypted_file