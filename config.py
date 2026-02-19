import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"

TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

SPEAKERS = {
    "elon_musk": {
        "name": "Elon Musk",
        "twitter_handle": "elonmusk",
    },
    "sam_altman": {
        "name": "Sam Altman",
        "twitter_handle": "sama",
    },
    "dario_amodei": {
        "name": "Dario Amodei",
        "twitter_handle": "DarioAmodei",
    },
    "mark_zuckerberg": {
        "name": "Mark Zuckerberg",
        "twitter_handle": "faboringd",
    },
}

REQUEST_DELAY = 2  # seconds between requests
REQUEST_TIMEOUT = 30
USER_AGENT = "CEOArena-DataCollector/1.0 (Research Project)"
