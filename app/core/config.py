from pydantic_settings import BaseSettings
import ctranslate2

class Settings(BaseSettings):
    PROJECT_NAME: str = "Sentiric LLM Local Service"
    API_V1_STR: str = "/api/v1"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    LLM_LOCAL_SERVICE_HTTP_PORT: int = 16060
    LLM_LOCAL_SERVICE_GRPC_PORT: int = 16061
    LLM_LOCAL_SERVICE_METRICS_PORT: int = 16062
    # --- DEĞİŞİKLİK BURADA ---
    LLM_LOCAL_SERVICE_MODEL_NAME: str = "microsoft/Phi-3-mini-4k-instruct"
    # LLM_LOCAL_SERVICE_MODEL_NAME: str = "microsoft/Phi-4-mini-instruct"
    LLM_LOCAL_SERVICE_DEVICE: str = "auto"
    LLM_LOCAL_SERVICE_COMPUTE_TYPE: str = "auto"
    
    def get_device(self) -> str:
        if self.LLM_LOCAL_SERVICE_DEVICE == "auto":
            try:
                return "cuda" if "cuda" in ctranslate2.get_supported_compute_types("cuda") else "cpu"
            except Exception:
                return "cpu"
        return self.LLM_LOCAL_SERVICE_DEVICE

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()