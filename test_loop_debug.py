#!/usr/bin/env python3

import sys
sys.path.insert(0, '/home/dennis/git-repos/musicdb')

# Simulate what happens in the loop when we have a continue statement
print("Testing loop with continue behavior...")

retries = 3
attempt = 1

for attempt in range(1, retries + 1):
    print(f"Attempt {attempt}")
    
    # Simulate an error condition like HTTPError
    if attempt == 1:
        print("Simulating HTTP 429 error...")
        # This would normally be: raise HTTPError(429, "Rate limited")
        
        # We want to simulate retry behavior - so we need to continue to next iteration 
        print("Would call time.sleep and then continue (but this doesn't work)")
        break  # Simulating the issue
    else:
        print("Success!")
    
print(f"Loop finished. Final attempt value: {attempt}")

# Now let's simulate a working version
print("\nTesting with fixed approach...")
def test_working_approach():
    retries = 3
    for attempt in range(1, retries + 1):
        print(f"Attempt {attempt}")
        
        if attempt == 1:
            print("Simulating HTTP 429 error...")
            # Simulate: continue would be here (but that's the problem)
            # What should happen is we just let it go to next iteration
            pass
        else:
            print("Success!")
            break

test_working_approach()