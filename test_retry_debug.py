#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

from unittest.mock import Mock, patch
from discogs_client.exceptions import HTTPError
from ingestion.fetch_release import fetch_release

print("Starting test...")

# Create a side effect that raises error first time, then returns success
mock_release = Mock()
mock_release.data = {"id": 12345, "title": "Test Release"}

def debug_side_effect(*args, **kwargs):
    print(f"DEBUG: mock_client.release called with args={args}, kwargs={kwargs}")
    
    # First call raises HTTPError, second succeeds 
    if debug_side_effect.call_count == 0:
        debug_side_effect.call_count += 1
        raise HTTPError(429, "Rate limited")
    else:
        return mock_release

debug_side_effect.call_count = 0

mock_client = Mock()
mock_client.release.side_effect = debug_side_effect

print("About to run with patches...")
with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
    with patch('time.sleep') as mock_sleep:
        print("Calling fetch_release(12345)...")
        result = fetch_release(12345)
        print(f"Result: {result}")
        print(f"Call count to release(): {mock_client.release.call_count}")
        print(f"Sleep called?: {mock_sleep.called}")

print("Done.")