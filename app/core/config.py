from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentiric LLM Local Service"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    LLM_LOCAL_SERVICE_HTTP_PORT: int = 16060
    LLM_LOCAL_SERVICE_GRPC_PORT: int = 16061
    LLM_LOCAL_SERVICE_METRICS_PORT: int = 16062

    # --- NİHAİ DEĞİŞİKLİK ---
    # GPU'da vLLM+AWQ ile çalışacak, önceden quantize edilmiş modeli kullanıyoruz.
    # CPU tarafı, bu modelin orijinal versiyonu olan 'microsoft/Phi-3-mini-4k-instruct'
    # adını tokenizer'ı bulmak için kullanacak ve sorunsuz çalışmaya devam edecektir.
    LLM_LOCAL_SERVICE_MODEL_NAME: str = "TheBloke/Phi-3-mini-4k-instruct-AWQ"
    
    LLM_LOCAL_SERVICE_DEVICE: str = "auto"

    VLLM_GPU_MEMORY_UTILIZATION: float = 0.90
    VLLM_DOWNLOAD_DIR: str = "/app/model-cache"

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()