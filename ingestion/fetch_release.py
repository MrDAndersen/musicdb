import time
from discogs_client.exceptions import HTTPError
from ingestion.discogs_client import get_discogs_client

def fetch_release(release_id: int, retries=3):
    # Validate input - release_id must be a positive integer
    if not isinstance(release_id, int) or release_id <= 0:
        return None
    
    d = get_discogs_client()
    
    for attempt in range(1, retries + 1):
        try:
            release = d.release(release_id)
            _ = release.title # hydrating the object to catch potential errors early
            
            return release.data
            
        except HTTPError as e:
            
            # Rate limit or server error → retry
            if e.status_code in (429, 500, 503, 504):
                sleep_time = attempt * 2
                print(f"Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            
            # Other HTTP errors → do not retry
            return None
            
        except Exception as e:
            return None
    
    print(f"[FAILED] {release_id} after {retries} retries")
    return None
