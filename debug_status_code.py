#!/usr/bin/env python3

from unittest.mock import Mock
from discogs_client.exceptions import HTTPError

# Test exactly how the error object looks
error = HTTPError(429, "Rate limited")
print(f"Error type: {type(error)}")
print(f"Error status_code attribute: {getattr(error, 'status_code', 'NO STATUS CODE')}")
print(f"Error args: {error.args}")

# Check if we can access the code in a different way
try:
    print(f"Error.code: {error.code}")
except AttributeError as e:
    print(f"No .code attribute: {e}")

try:
    # This is how HTTPError might be structured
    print("Looking for status_code or similar...")
    for attr_name in dir(error):
        if 'status' in attr_name.lower() or 'code' in attr_name.lower():
            value = getattr(error, attr_name)
            print(f"  {attr_name}: {value}")
except Exception as e:
    print(f"Error accessing attributes: {e}")

# Test a more comprehensive error access
print("\n--- Trying to replicate the exact same scenario ---")
mock_release = Mock()
mock_release.data = {"id": 12345, "title": "Test Release"}

mock_client = Mock()  
mock_client.release.side_effect = [
    HTTPError(429, "Rate limited"),
    mock_release
]

# Test calling it directly to see what happens
try:
    result = mock_client.release(12345)
    print(f"Unexpected success: {result}")
except HTTPError as e:
    print(f"Catched error details:")
    print(f"  Exception type: {type(e)}")
    print(f"  Exception args: {e.args}")
    
    # Try different ways to access status
    if hasattr(e, 'status_code'):
        print(f"  Status code via .status_code: {e.status_code}")
        
    if hasattr(e, 'code'):
        print(f"  Code via .code: {e.code}")
