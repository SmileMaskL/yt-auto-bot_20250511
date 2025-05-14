# scripts/content_generator.py
import os
import sys
import json
import base64
import logging
import random
from typing import List, Dict, Any
from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletion
from openai.types import CompletionUsage

# Configure module-specific logger
logger = logging.getLogger(__name__)
if not logger.handlers: # Setup handlers only once
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(name)s] %(message)s")
    
    # File handler for content_gen.log
    file_handler = logging.FileHandler("content_gen.log", mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Stream handler for console output
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

class OpenAIKeyManager:
    """Manages loading and validation of OpenAI API keys from environment variables."""
    def __init__(self, env_var_name: str = "OPENAI_API_KEYS_BASE64"):
        self.env_var_name = env_var_name
        self.keys: List[str] = self._load_and_validate_keys()
        if not self.keys:
             raise EnvironmentError("No valid OpenAI API keys were loaded.")
        logger.info(f"🔑 OpenAIKeyManager initialized with {len(self.keys)} API key(s).")

    def _load_and_validate_keys(self) -> List[str]:
        encoded_keys = os.environ.get(self.env_var_name, "").strip()

        if not encoded_keys:
            logger.error(f"🚨 Environment variable '{self.env_var_name}' is not set or is empty.")
            raise EnvironmentError(f"🚨 Environment variable '{self.env_var_name}' must be set.")

        try:
            decoded_bytes = base64.b64decode(encoded_keys, validate=True)
            decoded_str = decoded_bytes.decode('utf-8')
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            logger.error(f"🚨 Failed to decode Base64 string from '{self.env_var_name}': {e}. Check encoding.")
            raise ValueError(f"Invalid Base64 content in '{self.env_var_name}'.") from e

        try:
            parsed_keys = json.loads(decoded_str)
        except json.JSONDecodeError as e:
            logger.error(f"🚨 Failed to parse JSON from decoded API keys string: {e}. Decoded string (partial): '{decoded_str[:100]}...'")
            raise ValueError(f"API keys in '{self.env_var_name}' are not valid JSON.") from e

        if not isinstance(parsed_keys, list) or not parsed_keys:
            logger.error("🚨 Parsed API keys are not a list or the list is empty.")
            raise TypeError("API keys must be provided as a non-empty JSON list.")

        valid_keys: List[str] = []
        for i, key in enumerate(parsed_keys):
            if not isinstance(key, str) or not key.startswith("sk-"):
                logger.warning(f"⚠️ Invalid API key format at index {i}. Key (partial): '{str(key)[:5]}...'. Must be a string starting with 'sk-'. Skipping.")
                continue
            if len(key) < 20: # Basic sanity check for key length
                 logger.warning(f"⚠️ API key at index {i} seems too short. Key (partial): '{str(key)[:10]}...'. Skipping.")
                 continue
            valid_keys.append(key)
        
        if not valid_keys:
            logger.error("🚨 No valid API keys found after validation.")
            raise ValueError("No valid OpenAI API keys were found in the provided list.")

        logger.info(f"✅ Successfully loaded and validated {len(valid_keys)} OpenAI API key(s).")
        return valid_keys

    def get_random_key(self) -> str:
        if not self.keys:
            raise EnvironmentError("No API keys available to choose from.")
        return random.choice(self.keys)

class ContentGenerator:
    """Generates content using OpenAI's chat completion API."""
    def __init__(self, key_manager: OpenAIKeyManager, model: str = "gpt-4-turbo-preview"): # Use a more recent model if available
        self.key_manager = key_manager
        self.model = model
        self.default_params: Dict[str, Any] = {
            "temperature": 0.7,
            "max_tokens": 2000, # Adjust as needed
            "top_p": 1.0,
            # "frequency_penalty": 0.0,
            # "presence_penalty": 0.0,
        }
        logger.info(f"🤖 ContentGenerator initialized for model '{self.model}'.")

    def _get_client(self) -> OpenAI:
        return OpenAI(api_key=self.key_manager.get_random_key(), timeout=60.0)


    def generate_text(self, prompt: str, system_message: str = None, custom_params: Dict[str, Any] = None) -> str:
        """
        Generates text content based on a given prompt.
        """
        client = self._get_client()
        current_params = {**self.default_params, **(custom_params or {})}
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        logger.info(f"➡️ Generating content with prompt (first 100 chars): '{prompt[:100]}...'")
        logger.debug(f"Full prompt: {prompt}")
        logger.debug(f"System message: {system_message}")
        logger.debug(f"API call parameters: {current_params}")

        try:
            response: ChatCompletion = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **current_params
            )
            
            content = response.choices[0].message.content
            usage = response.usage
            
            if usage:
                self._log_token_usage(usage)
            
            if not content or content.isspace():
                logger.warning("⚠️ OpenAI API returned empty or whitespace content.")
                raise ValueError("Generated content is empty.")

            logger.info(f"⬅️ Content generated successfully (length: {len(content)}).")
            logger.debug(f"Generated content (first 100 chars): '{content[:100]}...'")
            return content.strip()

        except OpenAIError as e:
            logger.error(f"❌ OpenAI API error during content generation: {e}")
            raise # Re-raise after logging for higher-level handling
        except Exception as e:
            logger.error(f"❌ Unexpected error during content generation: {e}")
            raise

    def _log_token_usage(self, usage: CompletionUsage):
        if usage:
            logger.info(
                f"📊 Token usage: Prompt={usage.prompt_tokens}, "
                f"Completion={usage.completion_tokens}, Total={usage.total_tokens}"
            )

# Example usage for direct testing of this module
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG) # More verbose for direct testing
    logger.info("Running content_generator.py directly for testing...")
    try:
        # This expects OPENAI_API_KEYS_BASE64 to be set in your environment
        key_manager = OpenAIKeyManager()
        generator = ContentGenerator(key_manager=key_manager)
        
        test_query = "Explain the concept of quantum entanglement in simple terms for a YouTube short video script."
        system_msg = "You are a helpful assistant that creates engaging and easy-to-understand content for YouTube videos."
        
        generated_content = generator.generate_text(prompt=test_query, system_message=system_msg)
        
        print("\n" + "="*20 + " Generated Content " + "="*20)
        print(generated_content)
        print("="*60 + "\n")
        
    except EnvironmentError as e:
        logger.error(f"Setup error: {e}")
        print(f"Error: {e}. Please ensure OPENAI_API_KEYS_BASE64 environment variable is correctly set.")
    except Exception as e:
        logger.error(f"An error occurred during the test: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}")
