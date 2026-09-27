#!/usr/bin/env python3
"""
Basic unit tests for fetch_release function.
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
    
    # Make the client raise an exception when trying to fetch
    mock_client.release.side_effect = Exception("Not found")
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(99999)
        
        # Should return None for not found releases
        assert result is None


def test_fetch_release_no_id():
    """Test handling of invalid input (no ID)"""
    mock_client = Mock()
    
    with patch('ingestion.fetch_release.get_discogs_client', return_value=mock_client):
        result = fetch_release(None)
        
        # Should return None for invalid input
        assert result is None


if __name__ == "__main__":
    # Run the tests if script is run directly
    test_fetch_release_success()
    print("✓ test_fetch_release_success passed")
    
    test_fetch_release_not_found() 
    print("✓ test_fetch_release_not_found passed")
    
    test_fetch_release_no_id()
    print("✓ test_fetch_release_no_id passed")
    
    print("\nBasic tests passed! ✓")