import logging
import sys

from pythonjsonlogger import jsonlogger

logger = logging.getLogger("incident_ai")

logger.setLevel(logging.INFO)

stream_handler = logging.StreamHandler(sys.stdout)

formatter = jsonlogger.JsonFormatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
)

stream_handler.setFormatter(formatter)

logger.addHandler(stream_handler)