#!/usr/bin/env python3
"""
Retry logic Unit tests for fetch_release function - Part 1.
These tests mock the Discogs API to avoid external dependencies during testing.
"""

import sys
from unittest.mock import Mock, patch
from discogs_client.exceptions import HTTPError

# Add the project root to path so we can import modules
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

from ingestion.fetch_release import fetch_release


def test_fetch_release_http_429_retry():
    """Test retry logic for HTTP 429 error"""
    # Mock the Discogs client to raise an HTTPError with status code 429
    mock_client = Mock()
    
    # First call raises HTTPError, second succeeds 
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release"}
    
    # Create a side effect that raises error first time, then returns success
    mock_client.release.side_effect = [
        HTTPError(429, "Rate limited"),
        mock_release
    ]
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        with patch('time.sleep') as mock_sleep:
            result = fetch_release(12345)
            
            # Should have retried once (attempt 1 failed, attempt 2 succeeded)  
            assert result == {"id": 12345, "title": "Test Release"}
            assert mock_client.release.call_count == 2
            mock_sleep.assert_called_once_with(2)  # First retry waits 2 seconds


def test_fetch_release_max_retries_exceeded():
    """Test that max retries are properly enforced"""
    mock_client = Mock()
    
    # Make it always raise an exception to simulate failure
    mock_client.release.side_effect = HTTPError(429, "Rate limited")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        with patch('time.sleep') as mock_sleep:
            result = fetch_release(12345, retries=3)
            
            # Should have tried 3 times and failed
            assert result is None
            assert mock_client.release.call_count == 3


def test_fetch_release_http_500_retry():
    """Test retry logic for HTTP 500 error"""
    mock_client = Mock()
    
    # First call raises HTTPError, second succeeds 
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release"}
    
    # Create a side effect that raises error first time, then returns success
    mock_client.release.side_effect = [
        HTTPError(500, "Internal Server Error"),
        mock_release
    ]
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        with patch('time.sleep') as mock_sleep:
            result = fetch_release(12345)
            
            # Should have retried once (attempt 1 failed, attempt 2 succeeded)  
            assert result == {"id": 12345, "title": "Test Release"}
            assert mock_client.release.call_count == 2
            mock_sleep.assert_called_once_with(2)


if __name__ == "__main__":
    # Run the tests if script is run directly
    test_fetch_release_http_429_retry()
    print("✓ test_fetch_release_http_429_retry passed")
    
    test_fetch_release_max_retries_exceeded()
    print("✓ test_fetch_release_max_retries_exceeded passed")
    
    test_fetch_release_http_500_retry()
    print("✓ test_fetch_release_http_500_retry passed")
    
    print("\nRetry tests part 1 passed! ✓")