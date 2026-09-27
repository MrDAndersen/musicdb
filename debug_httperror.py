#!/usr/bin/env python3

from discogs_client.exceptions import HTTPError

# Test what happens with different error creation methods 
print("=== Testing direct HTTPError ===")
try:
    raise HTTPError(429, "Rate limited")
except HTTPError as e:
    print(f"Direct HTTPError - args: {e.args}")
    print(f"args[0] type: {type(e.args[0])} repr: {repr(e.args[0])}")
    
print("\n=== Testing with string message ===")
try:
    # This is how it might be constructed in discogs client
    error_msg = "Rate limited: 429"
    raise HTTPError(error_msg, 429)
except HTTPError as e:
    print(f"String msg - args: {e.args}")
    print(f"args[0] type: {type(e.args[0])} repr: {repr(e.args[0])}")

print("\n=== Testing what our code should do ===")
try:
    raise HTTPError(429, "Rate limited")
except HTTPError as e:
    # Let's simulate exactly how we extract it
    error_status_code = None
    
    if hasattr(e, 'status_code') and e.status_code is not None:
        error_status_code = e.status_code
    else:
        # Check the arguments (discogs client uses status_code, message format)
        print(f"e.args: {e.args}, len: {len(e.args)}")
        if len(e.args) >= 2:
            try:
                error_status_code = int(e.args[0])  # status code should be first arg
                print(f"Got status code from args[0]: {error_status_code}")
            except (ValueError, TypeError):
                pass 
    
    print(f"Final status code: {error_status_code}")
