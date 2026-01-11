import sys
from loguru import logger

# 移除默认日志处理器
logger.remove()

# 添加自定义日志格式
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True
)

# 添加文件日志（可选）
# logger.add("logs/app.log", rotation="10 MB", retention="30 days", level="DEBUG")

# 导出 logger 实例
get_logger = logger