from tenacity import *
import logging

class RetryEngine:
    """지능형 재시도 시스템 1.1"""
    
    def __init__(self, max_retries: int = 3):
        self.retrier = Retrying(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=30),
            retry=retry_if_exception_type(RetryableError),
            before_sleep=before_sleep_log(logging.getLogger(), logging.WARNING),
            reraise=True
        )

    def execute(self, func, *args, **kwargs):
        return self.retrier(func, *args, **kwargs)

class RetryableError(Exception):
    """복구 가능 오류 분류"""
    def __init__(self, message):
        super().__init__(f"🛠️ 자동 복구 시도: {message}")
