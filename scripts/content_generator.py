import logging
from openai import OpenAI
from scripts.utils.key_rotator import KeyManager
from scripts.utils.error_handler import RetryEngine, RetryableError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, encoded_keys: str):
        self.key_manager = KeyManager(encoded_keys)
        self.retry_engine = RetryEngine()

    def generate_text(self, prompt: str) -> str:
        def _generate():
            key = self.key_manager.select_key()
            client = OpenAI(api_key=key)
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "system", "content": "You are a helpful assistant."},
                              {"role": "user", "content": prompt}]
                )
                self.key_manager.update_usage(key, success=True)
                return response.choices[0].message.content
            except Exception as e:
                self.key_manager.update_usage(key, success=False)
                raise RetryableError(str(e))

        return self.retry_engine.execute(_generate)
