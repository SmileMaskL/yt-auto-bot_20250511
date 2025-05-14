import os
import base64
import json

class QuantumKeyVault:
    """10개 API 키 자동 순환 시스템"""
    
    def __init__(self):
        self.keys = self._decrypt_keys()
        self.index = 0

    def _decrypt_keys(self):
        encrypted = os.getenv("ENCRYPTED_KEYS")
        return json.loads(base64.b64decode(encrypted))
    
    def get_key(self):
        current_key = self.keys[self.index]
        self.index = (self.index + 1) % 10
        return current_key

    def emergency_rotate(self):
        self.index = (self.index + 5) % 10  # 긴급 순환
