import grpc
import structlog
import asyncio
from app.services.llm_engine import LLMEngine
from app.core.config import settings
from sentiric.llm.v1 import local_pb2, local_pb2_grpc

logger = structlog.get_logger(__name__)

class LLMLocalService(local_pb2_grpc.LLMLocalServiceServicer):
    def __init__(self, engine: LLMEngine):
        self.engine = engine

    async def LocalGenerateStream(
        self,
        request: local_pb2.LocalGenerateStreamRequest,
        context: grpc.aio.ServicerContext,
    ):
        try:
            if not self.engine.model_loaded:
                await context.abort(grpc.StatusCode.UNAVAILABLE, "Model is not ready.")
            if not request.prompt or not request.prompt.strip():
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Prompt cannot be empty.")
            for token in self.engine.generate_stream(request.prompt):
                yield local_pb2.LocalGenerateStreamResponse(token=token)
        except asyncio.CancelledError:
            logger.warning("Stream cancelled by client.", peer=context.peer())
        except Exception:
            logger.error("Unhandled exception during gRPC stream generation.", exc_info=True)
            await context.abort(grpc.StatusCode.INTERNAL, "An internal error occurred during stream generation.")

async def serve(engine: LLMEngine) -> grpc.aio.Server:
    server = grpc.aio.server()
    local_pb2_grpc.add_LLMLocalServiceServicer_to_server(LLMLocalService(engine), server)
    listen_addr = f"[::]:{settings.LLM_LOCAL_SERVICE_GRPC_PORT}"
    server.add_insecure_port(listen_addr)
    logger.info("Starting gRPC server...", address=listen_addr)
    await server.start()
    return server