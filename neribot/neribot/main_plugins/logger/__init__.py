from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger as logger_
from nonebot.log import default_filter, default_format

LOG_PATH = Path(__file__).parent / "logs"
# WARNING 级别及以上日志
logger_.add(
    LOG_PATH / f"warning_{datetime.now().date()}.log",
    level="WARNING",
    rotation="00:00",
    format=default_format,
    filter=default_filter,
    retention=timedelta(days=30),
)

