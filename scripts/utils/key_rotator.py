import base64
import json
import random
from datetime import datetime
from typing import List, Dict

class KeyManager:
    """API 키 관리 시스템 1.1 (실시간 모니터링)"""
    
    KEY_HISTORY = {}
    
    def __init__(self, encoded_keys: str):
        self.keys = self._decode(encoded_keys)
        self._init_history()

    def _decode(self, encoded: str) -> List[str]:
        decoded = base64.b64decode(encoded).decode('utf-8')
        return json.loads(decoded)

    def _init_history(self):
        for key in self.keys:
            key_id = self._generate_id(key)
            if key_id not in self.KEY_HISTORY:
                self.KEY_HISTORY[key_id] = {
                    'success': 0,
                    'fail': 0,
                    'last_used': None,
                    'quota': 100
                }

    def _generate_id(self, key: str) -> str:
        return f"key_{hash(key[-8:]) % 1000:04d}"

    def select_key(self) -> str:
        active_keys = [
            k for k in self.keys 
            if self.KEY_HISTORY[self._generate_id(k)]['quota'] > 0
        ]
        return random.choice(active_keys)

    def update_usage(self, key: str, success: bool):
        key_id = self._generate_id(key)
        if success:
            self.KEY_HISTORY[key_id]['success'] += 1
            self.KEY_HISTORY[key_id]['quota'] -= 1
        else:
            self.KEY_HISTORY[key_id]['fail'] += 1
        self.KEY_HISTORY[key_id]['last_used'] = datetime.now().isoformat()
