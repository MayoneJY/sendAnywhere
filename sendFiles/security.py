from cryptography.fernet import Fernet
from .key import key
import hashlib

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

def generate_sha256_hash(input_data):
    # 입력 데이터를 바이트로 인코딩.
    if isinstance(input_data, str):
        input_data = input_data.encode('utf-8')

    # SHA-256 해시 객체 생성
    sha256_hash = hashlib.sha256()

    # 입력 데이터를 해시 객체에 추가
    sha256_hash.update(input_data)

    # 해시 결과를 16진수 문자열로 반환
    return sha256_hash.hexdigest()