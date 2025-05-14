# scripts/content_generator.py
# [주의사항] 실행 전 OPENAI_API_KEYS_BASE64 환경변수 설정 필수

import os
import sys
import json
import base64
import logging
import random
from typing import List
from openai import OpenAI
from openai.types import CompletionUsage

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("content_gen.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

class OpenAIKeyManager:
    """API 키 관리 및 검증 클래스"""
    
    def __init__(self):
        self.keys = self._load_and_validate_keys()

    def _load_and_validate_keys(self) -> List[str]:
        encoded = os.environ.get("OPENAI_API_KEYS_BASE64", "")
        
        if not encoded:
            raise EnvironmentError("🚨 OPENAI_API_KEYS_BASE64 환경변수 미설정")
        
        if len(encoded) < 20:
            raise ValueError(f"잘못된 Base64 길이 ({len(encoded)}/20 최소)")
        
        try:
            decoded = base64.b64decode(encoded).decode('utf-8')
            keys = json.loads(decoded)
            
            if not isinstance(keys, list) or len(keys) == 0:
                raise TypeError("API 키 리스트 형식 오류")
                
            for idx, key in enumerate(keys):
                if not key.startswith("sk-"):
                    raise ValueError(f"{idx+1}번 키 형식 오류 ('sk-' 접두사 필요)")
                    
            logging.info(f"✅ {len(keys)}개의 API 키 검증 완료")
            return keys
            
        except Exception as e:
            logging.error(f"키 디코딩 실패: {str(e)}")
            raise

class ContentGenerator:
    """AI 기반 콘텐츠 생성 핵심 클래스"""
    
    def __init__(self, model: str = "gpt-4-turbo"):
        self.key_manager = OpenAIKeyManager()
        self.client = OpenAI(api_key=random.choice(self.key_manager.keys))
        self.model = model
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 2000,
            "top_p": 1.0
        }

    def generate(
        self,
        query: str,
        format_type: str = "markdown",
        language: str = "korean"
    ) -> str:
        """
        AI 콘텐츠 생성 메인 메서드
        Args:
            query: 생성 요청 내용
            format_type: 출력 형식 (markdown/html/plain)
            language: 출력 언어
        Returns:
            생성된 콘텐츠 문자열
        """
        prompt = self._build_prompt(query, format_type, language)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                **self.default_params
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            self._log_usage(usage)
            
            self._validate_content(content, format_type)
            return content
            
        except Exception as e:
            logging.error(f"생성 실패: {str(e)}")
            raise

    def _build_prompt(self, query: str, fmt: str, lang: str) -> str:
        return f"""다음 조건을 정확히 준수해 주세요:
1. 주제: {query}
2. 출력 형식: {fmt}
3. 각 항목 3문장 요약
4. 전문 용어 설명 포함
5. 언어: {lang}
6. 창의적이고 흥미로운 표현 사용"""

    def _validate_content(self, content: str, fmt: str):
        validation_rules = {
            "markdown": ("```markdown", 500),
            "html": ("<!DOCTYPE html>", 600),
            "plain": ("## 요약", 400)
        }
        
        marker, min_len = validation_rules.get(fmt, ("", 300))
        
        if len(content) < min_len:
            raise ValueError(f"콘텐츠 길이 부족 ({len(content)}/{min_len})")
        if fmt != "plain" and marker not in content:
            raise ValueError(f"{fmt} 형식 마커 누락")
        logging.info("✅ 콘텐츠 검증 통과")

    def _log_usage(self, usage: CompletionUsage):
        log_msg = (
            f"토큰 사용량: "
            f"입력 {usage.prompt_tokens} / "
            f"출력 {usage.completion_tokens} / "
            f"총계 {usage.total_tokens}"
        )
        logging.info(log_msg)

def main():
    """CLI 실행 인터페이스"""
    try:
        generator = ContentGenerator()
        
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            result = generator.generate(query)
            print("\n" + "="*50)
            print(result)
            print("="*50 + "\n")
        else:
            print("사용법: python content_generator.py [생성할 주제]")
            
    except Exception as e:
        logging.error(f"실행 오류: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
