#!/usr/bin/env python3
"""
Retry logic Unit tests for fetch_release function - Part 2.
These tests mock the Discogs API to avoid external dependencies during testing.
"""

import sys
from unittest.mock import Mock, patch
from discogs_client.exceptions import HTTPError

# Add the project root to path so we can import modules
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

from ingestion.fetch_release import fetch_release


def test_fetch_release_http_503_retry():
    """Test retry logic for HTTP 503 error"""
    mock_client = Mock()
    
    # First call raises HTTPError, second succeeds 
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release"}
    
    # Create a side effect that raises error first time, then returns success
    mock_client.release.side_effect = [
        HTTPError(503, "Service Unavailable"),
        mock_release
    ]
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        with patch('time.sleep') as mock_sleep:
            result = fetch_release(12345)
            
            # Should have retried once (attempt 1 failed, attempt 2 succeeded)  
            assert result == {"id": 12345, "title": "Test Release"}
            assert mock_client.release.call_count == 2
            mock_sleep.assert_called_once_with(2)


def test_fetch_release_http_504_retry():
    """Test retry logic for HTTP 504 error"""
    mock_client = Mock()
    
    # First call raises HTTPError, second succeeds 
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release"}
    
    # Create a side effect that raises error first time, then returns success
    mock_client.release.side_effect = [
        HTTPError(504, "Gateway Timeout"),
        mock_release
    ]
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        with patch('time.sleep') as mock_sleep:
            result = fetch_release(12345)
            
            # Should have retried once (attempt 1 failed, attempt 2 succeeded)  
            assert result == {"id": 12345, "title": "Test Release"}
            assert mock_client.release.call_count == 2
            mock_sleep.assert_called_once_with(2)


def test_fetch_release_http_404_no_retry():
    """Test that HTTP 404 errors are not retried"""
    mock_client = Mock()
    
    # Make it raise a 404 error (should not be retried)
    mock_client.release.side_effect = HTTPError(404, "Not Found")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(12345)
        
        # Should fail immediately without retries
        assert result is None
        mock_client.release.assert_called_once_with(12345)


def test_fetch_release_http_403_no_retry():
    """Test that HTTP 403 errors are not retried"""
    mock_client = Mock()
    
    # Make it raise a 403 error (should not be retried)
    mock_client.release.side_effect = HTTPError(403, "Forbidden")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(12345)
        
        # Should fail immediately without retries
        assert result is None
        mock_client.release.assert_called_once_with(12345)


if __name__ == "__main__":
    # Run the tests if script is run directly
    test_fetch_release_http_503_retry()
    print("✓ test_fetch_release_http_503_retry passed")
    
    test_fetch_release_http_504_retry()
    print("✓ test_fetch_release_http_504_retry passed")
    
    test_fetch_release_http_404_no_retry()
    print("✓ test_fetch_release_http_404_no_retry passed")
    
    test_fetch_release_http_403_no_retry()
    print("✓ test_fetch_release_http_403_no_retry passed")
    
    print("\nRetry tests part 2 passed! ✓")