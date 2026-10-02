"""Defines the logger to be used by different files"""
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

LOG_FILE = "logs/app.log"


def get_logger(name: str) -> logging.Logger:
  """Create a module-level logger with a readable format."""
  logger = logging.getLogger(name)
  if not logger.handlers:
    std_out_handler = logging.StreamHandler(sys.stdout)
    # Ensure the parent directory exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
      os.makedirs(log_dir)
    # Setup file handlers
    file_handler = RotatingFileHandler(
      filename=LOG_FILE,
      maxBytes=5242880,  # 5 Megabytes (5 * 1024 * 1024)
      backupCount=3,
      encoding="utf-8")
    handlers = [std_out_handler, file_handler]
    log_format = "%(asctime)s | %(filename)s:%(lineno)d | %(name)-18s | %(funcName)s | %(levelname)-7s | %(message)s "
    date_format = "%Y-%m-%d %H:%M:%S"
    for handler in handlers:
      handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
      logger.addHandler(handler)
  logger.setLevel(logging.INFO)
  return logger
