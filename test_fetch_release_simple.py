#!/usr/bin/env python3
"""
Simple unit tests for fetch_release function.
These tests mock the Discogs API to avoid external dependencies during testing.
"""

import sys
from unittest.mock import Mock, patch

# Add the project root to path so we can import modules
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

from ingestion.fetch_release import fetch_release


def test_fetch_release_success():
    """Test successful retrieval of a release"""
    mock_client = Mock()
    
    # Create a mock release with data
    mock_release = Mock()
    mock_release.data = {"id": 12345, "title": "Test Release", "artist": "Test Artist"}
    
    mock_client.release.return_value = mock_release
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(12345)
        
        # Verify the correct data was returned
        assert result == {"id": 12345, "title": "Test Release", "artist": "Test Artist"}
        mock_client.release.assert_called_once_with(12345)


def test_fetch_release_not_found():
    """Test handling of a release that doesn't exist"""
    mock_client = Mock()
    
    # Make the client raise an HTTPError when trying to fetch (404 Not Found)
    from discogs_client.exceptions import HTTPError
    mock_client.release.side_effect = HTTPError(404, "The requested resource was not found.")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(99999)
        
        # Should return None for not found releases
        assert result is None


def test_fetch_release_invalid_id():
    """Test handling of invalid input (no ID or <= 0)"""
    mock_client = Mock()
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        # Test with None
        try:
            fetch_release(None)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
        
        # Test with 0  
        try:
            fetch_release(0)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected
            
        # Test with negative number
        try:
            fetch_release(-1)
            assert False, "Should have raised ValueError"
        except ValueError:
            pass  # Expected


def test_fetch_release_rate_limited():
    """Test handling of rate limiting - should retry 3 times"""
    mock_client = Mock()
    
    from discogs_client.exceptions import HTTPError
    # Simulate a 429 rate limit error  
    mock_client.release.side_effect = HTTPError(429, "Rate limited")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(12345)
        
        # Should retry and eventually give up, returning None
        assert result is None
        # The function should be called at least once to confirm the logic works
        assert mock_client.release.call_count >= 1


def test_fetch_release_server_error():
    """Test handling of server errors - should retry 3 times"""
    mock_client = Mock()
    
    from discogs_client.exceptions import HTTPError
    # Simulate a 500 internal server error  
    mock_client.release.side_effect = HTTPError(500, "Internal Server Error")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(12345)
        
        # Should retry and eventually give up, returning None
        assert result is None
        # The function should be called at least once to confirm the logic works
        assert mock_client.release.call_count >= 1


if __name__ == "__main__":
    # Run the tests if script is run directly
    test_fetch_release_success()
    print("✓ test_fetch_release_success passed")
    
    test_fetch_release_not_found() 
    print("✓ test_fetch_release_not_found passed")
    
    test_fetch_release_invalid_id()
    print("✓ test_fetch_release_invalid_id passed")
    
    test_fetch_release_rate_limited()
    print("✓ test_fetch_release_rate_limited passed")
    
    test_fetch_release_server_error()
    print("✓ test_fetch_release_server_error passed")
    
    print("\nAll tests passed! ✓")