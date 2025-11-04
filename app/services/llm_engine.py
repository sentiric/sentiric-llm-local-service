import os
import structlog
import asyncio
from typing import Generator as PyGenerator
from ctranslate2 import Generator
from transformers import AutoTokenizer
from app.core.config import settings

logger = structlog.get_logger(__name__)

class LLMEngine:
    def __init__(self):
        self.generator: Generator | None = None
        self.tokenizer: AutoTokenizer | None = None
        self.model_loaded = False
        self.device = settings.get_device()
        self.compute_type = settings.LLM_LOCAL_SERVICE_COMPUTE_TYPE
        if self.compute_type == "auto":
            self.compute_type = "float16" if self.device == "cuda" else "int8"

    async def load_model(self):
        if self.model_loaded:
            return

        # Dockerfile tarafından sağlanan, önceden dönüştürülmüş modelin yolu
        ct2_model_path = "/app/model-cache/converted_model"
        # Tokenizer hala orijinal adıyla Hugging Face'den indirilecek (bu küçük bir işlemdir)
        tokenizer_name = settings.LLM_LOCAL_SERVICE_MODEL_NAME
        tokenizer_cache_path = "/app/model-cache/hf_tokenizer"

        try:
            logger.info("Loading pre-converted local LLM model...", path=ct2_model_path, device=self.device)
            self.generator = Generator(ct2_model_path, device=self.device)
            
            logger.info("Loading tokenizer...", tokenizer=tokenizer_name)
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, cache_dir=tokenizer_cache_path)
            
            self.model_loaded = True
            logger.info("✅ Local LLM model and tokenizer loaded successfully.")

        except Exception as e:
            logger.error("❌ Failed to load local LLM resources", error=str(e), exc_info=True)
            self.model_loaded = False

    def generate_stream(self, prompt: str) -> PyGenerator[str, None, None]:
        if not self.generator or not self.tokenizer:
            raise RuntimeError("Model is not loaded.")

        messages = [{"role": "user", "content": prompt}]
        try:
            prompt_formatted = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(prompt_formatted))
            
            step_results = self.generator.generate_tokens(
                tokens,
                sampling_temperature=0.6,
                max_length=1024,
                end_token=[self.tokenizer.eos_token_id] if self.tokenizer.eos_token_id is not None else []
            )

            for step in step_results:
                token_str = self.tokenizer.decode([step.token_id])
                yield token_str
        except Exception as e:
            logger.error("Token generation failed.", exc_info=True)
            yield "[HATA: Model yanıt üretemedi.]"