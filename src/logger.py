import logging
import os
from logging.handlers import RotatingFileHandler

# 路径计算（适配所有场景）
CURRENT_FILE_PATH = os.path.abspath(__file__)
SRC_DIR = os.path.dirname(CURRENT_FILE_PATH)
PROJECT_ROOT = os.path.dirname(SRC_DIR)

# 日志目录
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
LOG_FILE = os.path.join(LOG_DIR, "hr_rag_helper.log")

# 日志格式
LOG_FORMAT = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
)

def get_logger(name: str = "hr_rag") -> logging.Logger:
    """获取标准化日志实例（添加异常容错）"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 避免重复添加处理器
    if logger.handlers:
        return logger

    # 1. 控制台处理器（必加）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LOG_FORMAT)
    logger.addHandler(console_handler)

    # 2. 文件处理器（容错）
    try:
        os.makedirs(LOG_DIR, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=50 * 1024 * 1024,  # 50MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(LOG_FORMAT)
        logger.addHandler(file_handler)
        logger.info(f"✅ 日志文件初始化成功：{LOG_FILE}")
    except Exception as e:
        logger.warning(f"⚠️ 日志文件创建失败（仅控制台输出）：{str(e)}")

    return logger

# 全局日志对象
try:
    logger = get_logger()
    logger.info("✅ 全局日志初始化成功")
except Exception as e:
    logger = logging.getLogger("hr_rag_fallback")
    logger.setLevel(logging.INFO)
    fallback_handler = logging.StreamHandler()
    fallback_handler.setFormatter(LOG_FORMAT)
    logger.addHandler(fallback_handler)
    logger.error(f"❌ 日志兜底初始化：{str(e)}")