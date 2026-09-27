#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

from unittest.mock import Mock, patch
from discogs_client.exceptions import HTTPError

# Let's manually simulate the exact logic from fetch_release to see what happens
def debug_fetch_release(release_id: int, retries=3):
    print(f"Starting debug_fetch_release for {release_id}")
    
    # This is what get_discogs_client() does in real life  
    mock_client = Mock()
    
    # Set up the side effect like our test 
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release"}
    mock_release.title = "Test Release"
    
    mock_client.release.side_effect = [
        HTTPError(429, "Rate limited"),
        mock_release
    ]
    
    print("Client set up with side effect")
    
    for attempt in range(1, retries + 1):
        print(f"--- Attempt {attempt} ---")
        
        try:
            release = mock_client.release(release_id)
            print(f"SUCCESS: Got release data: {release.data}")
            
            return release.data
            
        except HTTPError as e:
            print(f"[HTTP ERROR] {release_id}: {e}")
            
            # Rate limit or server error → retry
            if e.status_code in (429, 500, 503, 504):
                sleep_time = attempt * 2
                print(f"Retrying in {sleep_time}s...")
                # Simulate time.sleep
                print("Sleep completed")
                print(f"About to continue - this should go back to loop!")
                continue
            
            # Other HTTP errors → do not retry
            print("Not a retryable error, returning None")
            return None
            
        except Exception as e:
            print(f"[ERROR] {release_id}: {e}")
            return None
    
    print(f"[FAILED] {release_id} after {retries} retries")
    return None

print("=== Manual simulation ===")
result = debug_fetch_release(12345)
print(f"Final result: {result}")

# Now let's actually test it with real patching
print("\n=== Real function test ===")

from ingestion.fetch_release import fetch_release

with patch('ingestion.fetch_release.get_discogs_client') as mock_get_client:
    # Set up our client mock 
    mock_client = Mock()
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release"}
    mock_release.title = "Test Release"
    
    mock_client.release.side_effect = [
        HTTPError(429, "Rate limited"),
        mock_release
    ]
    
    mock_get_client.return_value = mock_client
    
    with patch('time.sleep') as mock_sleep:
        print("Calling real fetch_release function...")
        result2 = fetch_release(12345)
        print(f"Real function result: {result2}")