import logging
import sys
import structlog
from app.core.config import settings

def setup_logging():
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    noisy_libraries = {
        "numba": logging.WARNING,
        "huggingface_hub": logging.WARNING,
        "filelock": logging.WARNING,
        "uvicorn.access": logging.WARNING,
        "urllib3": logging.WARNING,
    }
    for lib_name, level in noisy_libraries.items():
        logging.getLogger(lib_name).setLevel(level)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer() if settings.ENV == "development" else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        root_logger.setLevel(log_level)
        handler = logging.StreamHandler(sys.stdout)
        root_logger.addHandler(handler)