#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

from unittest.mock import Mock
from discogs_client.exceptions import HTTPError

# Test how side effects work with mock
print("Testing side effect behavior...")

mock_release = Mock()
mock_release.data = {"id": 12345, "title": "Test Release"}

# Create a side effect that raises error first time, then returns success
mock_client = Mock()
mock_client.release.side_effect = [
    HTTPError(429, "Rate limited"),
    mock_release
]

print("Side effect created")
print(f"Call 1 result:")
try:
    result1 = mock_client.release(12345)
    print(f"Success: {result1}")
except Exception as e:
    print(f"Exception: {e}")

print(f"Call 2 result:")
try:
    result2 = mock_client.release(12345)  
    print(f"Success: {result2}")
except Exception as e:
    print(f"Exception: {e}")

print("Done.")