from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.llm_engine import LLMEngine
from app.services.grpc_server import serve as serve_grpc

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("🚀 LLM Local Service starting up...")
    
    engine = LLMEngine()
    app.state.engine = engine
    
    # Modeli arka planda yükle
    import asyncio
    asyncio.create_task(engine.load_model())
    
    # gRPC sunucusunu başlat
    grpc_server = await serve_grpc(engine)
    app.state.grpc_server = grpc_server
    
    yield
    
    logger.info("🛑 LLM Local Service shutting down...")
    await app.state.grpc_server.stop(grace=1)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    lifespan=lifespan
)

@app.get("/health", tags=["Health"])
async def health_check():
    engine = app.state.engine
    status_code = 200 if engine.model_loaded else 503
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "healthy" if engine.model_loaded else "unhealthy",
            "model_ready": engine.model_loaded,
            "model_name": settings.LLM_LOCAL_SERVICE_MODEL_NAME,
            "device": engine.device
        }
    )