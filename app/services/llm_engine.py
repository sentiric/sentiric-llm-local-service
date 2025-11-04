import os
import structlog
import asyncio
import subprocess
import sys
from typing import Generator as PyGenerator
from ctranslate2 import Generator
from transformers import AutoTokenizer
from huggingface_hub import snapshot_download
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

        model_name = settings.LLM_LOCAL_SERVICE_MODEL_NAME
        model_cache_path = "/app/model-cache"
        ct2_model_path = os.path.join(model_cache_path, model_name.replace("/", "_") + f"_ct2_{self.compute_type}")

        try:
            # 1. Model zaten dönüştürülmüş mü diye kontrol et
            if not os.path.exists(os.path.join(ct2_model_path, "model.bin")):
                logger.warning("CTranslate2 modeli bulunamadı. İndirme ve dönüştürme işlemi başlatılıyor...", model=model_name)
                
                # 2. Hugging Face'den orijinal modeli indir (eğer yoksa)
                logger.info("Orijinal model indiriliyor...", model=model_name)
                # snapshot_download, dosyalar zaten varsa tekrar indirmez, bu yüzden güvenlidir.
                hf_model_path = snapshot_download(repo_id=model_name, cache_dir=model_cache_path, local_files_only=False)
                logger.info("Orijinal model indirildi.", path=hf_model_path)

                # 3. Modeli CTranslate2 formatına dönüştürmek için komut satırı aracını çalıştır
                logger.info("Model CTranslate2 formatına dönüştürülüyor...", output_path=ct2_model_path)
                
                command = [
                    "ct2-transformers-converter",
                    "--model", hf_model_path,
                    "--output_dir", ct2_model_path,
                    "--quantization", self.compute_type,
                    "--force"
                ]
                
                # subprocess'i çalıştır ve çıktısını logla
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    logger.error("Model dönüştürme başarısız!", stderr=stderr.decode())
                    raise RuntimeError("CTranslate2 model conversion failed.")
                else:
                    logger.info("Model başarıyla dönüştürüldü.", stdout=stdout.decode())

            # 4. Dönüştürülmüş modeli yükle
            logger.info("Loading local LLM model...", path=ct2_model_path, device=self.device, compute=self.compute_type)
            self.generator = Generator(ct2_model_path, device=self.device)
            # Tokenizer her zaman orijinal model adından yüklenir (bu işlem hızlıdır)
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model_loaded = True
            logger.info("✅ Local LLM model loaded successfully.")

        except Exception as e:
            logger.error("❌ Model yükleme veya dönüştürme sırasında kritik hata oluştu.", error=str(e), exc_info=True)
            self.model_loaded = False

    def generate_stream(self, prompt: str) -> PyGenerator[str, None, None]:
        if not self.generator or not self.tokenizer:
            raise RuntimeError("Model is not loaded.")

        # Phi-3 için doğru prompt formatı
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
            logger.error("Token üretimi sırasında hata oluştu.", exc_info=True)
            yield "[HATA: Model yanıt üretemedi.]"