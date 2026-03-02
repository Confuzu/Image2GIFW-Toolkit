import os
import logging

_configured = False

def setup_logging(log_dir=None, level=logging.DEBUG):
    """Configure logging once for the entire application.

    All modules use child loggers under 'image2gifw' which inherit this config.
    Call this once from main.py or from each module's standalone block.

    Args:
        log_dir: Directory for the log file. Defaults to the script directory.
        level: Logging level. Defaults to DEBUG.
    """
    global _configured
    if _configured:
        return logging.getLogger('image2gifw')

    if log_dir is None:
        log_dir = os.path.dirname(os.path.abspath(__file__))

    log_path = os.path.join(log_dir, "image2gifw.log")

    logger = logging.getLogger('image2gifw')
    logger.setLevel(level)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    _configured = True
    return logger
