import sys
from loguru import logger

from app.core.config import get_settings


def setup_logging():
    settings = get_settings()

    logger.remove()

    log_level = "DEBUG" if settings.DEBUG else "INFO"

    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level,
        colorize=True,
    )

    if settings.LOG_FILE:
        logger.add(
            settings.LOG_FILE,
            rotation="500 MB",
            retention="10 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level=log_level,
        )

    return logger
