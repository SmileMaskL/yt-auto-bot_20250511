import base64
import os
from cryptography.fernet import Fernet

class KeyManager:
    """10개 API 키 암호화 순환 시스템"""
    
    def __init__(self):
        self.keys = self._decrypt_keys()
        self.index = 0
        
    def _decrypt_keys(self):
        encrypted = base64.b64decode(os.getenv("ENCRYPTED_KEYS"))
        cipher = Fernet(os.getenv("FERNET_KEY"))
        return cipher.decrypt(encrypted).decode().split(",")
    
    def get_key(self):
        key = self.keys[self.index]
        self.index = (self.index + 1) % 10
        return key
