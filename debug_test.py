#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

from unittest.mock import Mock, patch
from discogs_client.exceptions import HTTPError
from ingestion.fetch_release import fetch_release

print('Testing manually...')

mock_client = Mock()
mock_release = Mock()
mock_release.data = {'id': 12345, 'title': 'Test Release'}

# Create a side effect that raises error first time, then returns success
mock_client.release.side_effect = [
    HTTPError(429, "Rate limited"),
    mock_release
]

with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
    result = fetch_release(12345)
    print(f'Result: {result}')