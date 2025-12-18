import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

error_log = LOG_DIR / "errors.log"

logger = logging.getLogger("myapp")
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(error_log, maxBytes=5_000_000, backupCount=5, encoding="utf-8")
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
