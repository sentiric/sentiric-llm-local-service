import structlog
import asyncio
from typing import Generator as PyGenerator
from app.core.config import settings

logger = structlog.get_logger(__name__)

class LLMEngine:
    def __init__(self):
        self.model_loaded = False
        self.device = settings.get_device()

    async def load_model(self):
        if self.model_loaded:
            return
        # Bu, bir sonraki adımda gerçek model yükleme mantığıyla değiştirilecek.
        logger.info("Simulating model load...", model=settings.LLM_LOCAL_SERVICE_MODEL_NAME, device=self.device)
        await asyncio.sleep(2) # Gerçekçi bir gecikme simülasyonu
        self.model_loaded = True
        logger.info("✅ Mock model loaded successfully.")

    def generate_stream(self, prompt: str) -> PyGenerator[str, None, None]:
        logger.info("Generating mock stream for prompt.", prompt=prompt)
        mock_response = [
            "Bu, ", "yerel ", "LLM ", "motorundan ", "gelen ",
            "bir ", "test ", "akışıdır.", "\n"
        ]
        for token in mock_response:
            yield token