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
        try:
            model_name = settings.LLM_LOCAL_SERVICE_MODEL_NAME
            # Not: CTranslate2 CLI ile modelin önceden dönüştürülmüş olması gerekir.
            # Örnek Komut:
            # ct2-transformers-converter --model microsoft/Phi-3-mini-4k-instruct --output_dir ./model-cache/microsoft_Phi-3-mini-4k-instruct_ct2 --quantization int8 --force
            model_path = f"/app/model-cache/{model_name.replace('/', '_')}_ct2"
            
            logger.info("Loading local LLM model...", model=model_name, path=model_path, device=self.device, compute=self.compute_type)
            
            self.generator = Generator(model_path, device=self.device, compute_type=self.compute_type)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model_loaded = True
            logger.info("✅ Local LLM model loaded successfully.")
        except Exception as e:
            logger.error("❌ Failed to load local LLM model", error=str(e), exc_info=True)
            self.model_loaded = False
            # Uygulamanın çökmemesi için hatayı yutuyoruz, healthcheck durumu bildirecek.

    def generate_stream(self, prompt: str) -> PyGenerator[str, None, None]:
        if not self.generator or not self.tokenizer:
            raise RuntimeError("Model is not loaded.")

        prompt_tokens = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(f"<|user|>\n{prompt}<|end|>\n<|assistant|>\n"))
        
        step_results = self.generator.generate_tokens(
            prompt_tokens,
            sampling_temperature=0.6,
            max_length=1024,
            end_token=[self.tokenizer.eos_token_id]
        )

        for step in step_results:
            token_id = step.token_id
            token_str = self.tokenizer.decode([token_id], skip_special_tokens=True)
            yield token_str