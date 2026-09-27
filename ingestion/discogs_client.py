from dotenv import load_dotenv
import os
import discogs_client
from pathlib import Path

def get_discogs_client():
    # Load .env from config/
    env_path = Path(__file__).parent.parent / "config" / ".env"
    load_dotenv(env_path)

    token = os.getenv("DISCOGS_TOKEN")
    if not token:
        raise RuntimeError("DISCOGS_TOKEN not found in .env")

    return discogs_client.Client(
        "MusicDBApp/1.0",
        user_token=token
    )
