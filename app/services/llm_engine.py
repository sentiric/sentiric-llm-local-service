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

    async def load_model(self):
        if self.model_loaded:
            return

        ct2_model_path = "/app/model-cache/converted_model"
        tokenizer_name = settings.LLM_LOCAL_SERVICE_MODEL_NAME

        try:
            # Modelin hazır olmasını bekle
            while not os.path.exists(os.path.join(ct2_model_path, "model.bin")):
                logger.warning("Dönüştürülmüş model bekleniyor...", path=ct2_model_path)
                await asyncio.sleep(5)

            logger.info("Loading pre-converted local LLM model...", path=ct2_model_path)
            self.generator = Generator(ct2_model_path, device=self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, cache_dir="/app/model-cache/hf_tokenizer")
            self.model_loaded = True
            logger.info("✅ Local LLM model and tokenizer loaded successfully.")
        except Exception as e:
            logger.error("❌ Failed to load local LLM resources", error=str(e), exc_info=True)
            self.model_loaded = False
    
    # generate_stream metodu aynı kalabilir...