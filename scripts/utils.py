import logging
from datetime import date
from dateutil.relativedelta import relativedelta
import config

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def calculate_age() -> str:
    """Calculates age based on BIRTHDAY configuration."""
    birth_date = date.fromisoformat(config.BIRTHDAY)
    today = date.today()
    diff = relativedelta(today, birth_date)
    return f"{diff.years}y {diff.months}m {diff.days}d"
