import structlog
import asyncio
import torch
from app.core.config import settings

logger = structlog.get_logger(__name__)

# Cihazı en başta bir kez tespit et
DEVICE = "cuda" if torch.cuda.is_available() and settings.LLM_LOCAL_SERVICE_DEVICE != "cpu" else "cpu"

# Cihaza göre gerekli kütüphaneleri import et
if DEVICE == "cuda":
    from vllm.engine.arg_utils import AsyncEngineArgs
    from vllm.engine.async_llm_engine import AsyncLLMEngine
    from vllm.sampling_params import SamplingParams
    from vllm.utils import random_uuid
else:
    from threading import Thread
    from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer

class LLMEngine:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.engine: 'AsyncLLMEngine' | None = None
        self.model_loaded = False
        self.device = DEVICE
        self.model_name = settings.LLM_LOCAL_SERVICE_MODEL_NAME
        self._engine_ready_event = asyncio.Event()

        logger.info(f"Cihaz '{self.device}' olarak ayarlandı. Uygun motor başlatılıyor...")

        if self.device == "cuda":
            try:
                engine_args = AsyncEngineArgs(
                    model=self.model_name,
                    trust_remote_code=True,
                    gpu_memory_utilization=settings.VLLM_GPU_MEMORY_UTILIZATION,
                    download_dir=settings.VLLM_DOWNLOAD_DIR,
                    # --- OPTİMİZASYON: Quantization'ı etkinleştiriyoruz ---
                    quantization="awq"
                )
                self.engine = AsyncLLMEngine.from_engine_args(engine_args)
            except Exception as e:
                logger.error("vLLM motoru başlatılırken kritik hata!", error=str(e), exc_info=True)
                self.engine = None
        else: # CPU durumu
            pass  # Yükleme işlemi load_model içinde yapılacak

    async def _check_vllm_status(self):
        if not self.engine: return
        while not await self.engine.is_ready():
            logger.warning("vLLM motoru hazırlanıyor, 5 saniye bekleniyor...")
            await asyncio.sleep(5)
        self.model_loaded = True
        self._engine_ready_event.set()
        logger.info("✅ vLLM motoru (GPU) başarıyla yüklendi ve servise hazır.")

    def _load_transformers_model_sync(self):
        try:
            logger.info("Loading Hugging Face model for CPU...", model=self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                cache_dir=settings.VLLM_DOWNLOAD_DIR,
                trust_remote_code=True
            )
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, cache_dir=settings.VLLM_DOWNLOAD_DIR)
            self.model_loaded = True
            self._engine_ready_event.set()
            logger.info("✅ Hugging Face (CPU) modeli başarıyla yüklendi ve servise hazır.")
        except Exception as e:
            logger.error("❌ Hugging Face (CPU) modeli yüklenirken hata oluştu", error=str(e), exc_info=True)

    async def load_model(self):
        if self.device == "cuda":
            asyncio.create_task(self._check_vllm_status())
        else:
            await asyncio.to_thread(self._load_transformers_model_sync)

    async def generate_stream(self, prompt: str):
        await self._engine_ready_event.wait()

        if self.device == "cuda" and self.engine:
            tokenizer = await self.engine.get_tokenizer()
            messages = [{"role": "user", "content": prompt}]
            final_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            
            sampling_params = SamplingParams(temperature=0.7, top_p=0.95, max_tokens=2048)
            request_id = f"sentiric-{random_uuid()}"
            results_generator = self.engine.generate(final_prompt, sampling_params, request_id)

            previous_text = ""
            async for request_output in results_generator:
                new_text = request_output.outputs[0].text
                yield new_text[len(previous_text):]
                previous_text = new_text
        
        elif self.device == "cpu" and self.model and self.tokenizer:
            streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
            messages = [{"role": "user", "content": prompt}]
            text_prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            inputs = self.tokenizer([text_prompt], return_tensors="pt")

            generation_kwargs = dict(**inputs, streamer=streamer, max_new_tokens=2048, temperature=0.7, do_sample=True)
            
            thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
            thread.start()

            for token in streamer:
                yield token
            
            thread.join()
        
        else:
            logger.error("generate_stream çağrıldı ancak uygun motor bulunamadı.")
            raise RuntimeError("No valid engine found for the current device.")