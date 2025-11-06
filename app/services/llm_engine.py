import os
import structlog
import asyncio
import time
from typing import Generator as PyGenerator, List
from ctranslate2 import Generator
from transformers import AutoTokenizer
from app.core.config import settings
from prometheus_client import Counter, Histogram

logger = structlog.get_logger(__name__)

GENERATED_TOKENS_COUNTER = Counter(
    "llm_local_generated_tokens_total",
    "Toplam üretilen token sayısı."
)
INFERENCE_LATENCY_HISTOGRAM = Histogram(
    "llm_local_inference_latency_seconds",
    "Token başına çıkarım gecikmesi (saniye).",
    buckets=[0.005, 0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5]
)

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
            while not os.path.exists(os.path.join(ct2_model_path, "model.bin")):
                logger.warning("Dönüştürülmüş model bekleniyor...", path=ct2_model_path)
                await asyncio.sleep(5)

            logger.info("Loading pre-converted CTranslate2 model...", path=ct2_model_path, device=self.device)
            self.generator = Generator(ct2_model_path, device=self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name, cache_dir="/app/model-cache/hf_tokenizer")
            self.model_loaded = True
            logger.info("✅ Local LLM model and tokenizer loaded successfully.")
        except Exception as e:
            logger.error("❌ Failed to load local LLM resources", error=str(e), exc_info=True)
            self.model_loaded = False
    
    def generate_stream(self, prompt: str) -> PyGenerator[str, None, None]:
        if not self.model_loaded or not self.tokenizer or not self.generator:
            raise RuntimeError("Model is not loaded.")
        
        # --- YENİ: PHI-4 SOHBET ŞABLONU UYGULAMASI ---
        # Gelen prompt'u modelin beklediği mesaj formatına dönüştür.
        messages = [{"role": "user", "content": prompt}]
        
        # Transformers tokenizer'ı kullanarak doğru formatlanmış prompt'u oluştur.
        # add_generation_prompt=True, modelin yanıt vermesi için gereken '<|assistant|>' 
        # gibi son token'ları ekler.
        formatted_prompt = self.tokenizer.apply_chat_template(
            messages, 
            tokenize=False, 
            add_generation_prompt=True
        )
        
        # Formatlanmış prompt'u CTranslate2'nin beklediği token listesine çevir.
        prompt_tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(formatted_prompt))
        # --- DEĞİŞİKLİK SONU ---

        step_results = self.generator.generate_tokens(
            prompt_tokens,
            sampling_temperature=0.7,
            max_length=4096, # Maksimum üretilecek token sayısını makul bir değerde tutalım
        )

        for step_result in step_results:
            start_time = time.time()
            
            # Bitiş token'ını (<|end|>) istemciye gönderme
            if step_result.token == "<|end|>":
                break

            yield step_result.token
            
            latency = time.time() - start_time
            INFERENCE_LATENCY_HISTOGRAM.observe(latency)
            GENERATED_TOKENS_COUNTER.inc()