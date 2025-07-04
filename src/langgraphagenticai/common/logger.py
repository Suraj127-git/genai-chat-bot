from logtail import LogtailHandler
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from environment variables
LOGTAIL_SOURCE_TOKEN = os.getenv('LOGTAIL_SOURCE_TOKEN')
LOGTAIL_HOST = os.getenv('LOGTAIL_HOST')

if not LOGTAIL_SOURCE_TOKEN or not LOGTAIL_HOST:
    raise ValueError('Logtail credentials not found in environment variables')

handler = LogtailHandler(
    source_token=LOGTAIL_SOURCE_TOKEN,
    host=LOGTAIL_HOST,
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = []
logger.addHandler(handler)
