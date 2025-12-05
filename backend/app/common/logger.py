from logtail import LogtailHandler
import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOGTAIL_SOURCE_TOKEN = os.getenv('LOGTAIL_SOURCE_TOKEN')
LOGTAIL_HOST = os.getenv('LOGTAIL_HOST')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []

if LOGTAIL_SOURCE_TOKEN and LOGTAIL_HOST:
    handler = LogtailHandler(
        source_token=LOGTAIL_SOURCE_TOKEN,
        host=LOGTAIL_HOST,
    )
    logger.addHandler(handler)
else:
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

