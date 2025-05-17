# error_handler.py (강화 버전)
import logging
from google.api_core import retry

class ErrorHandler:
    @retry.Retry(predicate=retry.if_exception_type(Exception))
    def api_call(self, func, *args):
        try:
            return func(*args)
        except Exception as e:
            self.rotate_api_key()
            logging.error(f"자동 복구 진행: {str(e)}")
            return func(*args)  # 최대 3회 재시도

    def rotate_api_key(self):
        # 10개 OpenAI 키 순환 사용
        current_key = os.environ['OPENAI_API_KEY']
        key_list = os.environ['OPENAI_API_KEYS'].split(',')
        new_index = (key_list.index(current_key) + 1) % 10
        os.environ['OPENAI_API_KEY'] = key_list[new_index]
