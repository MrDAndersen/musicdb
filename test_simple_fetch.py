#!/usr/bin/env python3

# Simple test for fetch_release function to verify it imports correctly
import sys
import os

# Add the current directory to Python path so we can import our modules  
sys.path.insert(0, '.')

try:
    from ingestion.fetch_release import fetch_release
    print("✓ Successfully imported fetch_release")
    
    # Test that function exists and is callable
    if callable(fetch_release):
        print("✓ fetch_release function is callable")
    else:
        print("✗ fetch_release is not callable")
        
    # Try to check the source code
    import inspect
    source = inspect.getsource(fetch_release)
    print(f"✓ Function has {len(source)} characters of source code")
    
except Exception as e:
    print(f"✗ Error importing fetch_release: {e}")
    import traceback
    traceback.print_exc()