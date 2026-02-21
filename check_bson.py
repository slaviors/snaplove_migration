#!/usr/bin/env python
"""Diagnostic script to check bson module installation"""

import sys

print("=" * 60)
print("BSON Module Diagnostic")
print("=" * 60)

# Check bson module
try:
    import bson
    print(f"✓ bson module found: {bson.__file__}")
    print(f"  Version: {getattr(bson, '__version__', 'unknown')}")
    print(f"\n  Available attributes:")
    attrs = [attr for attr in dir(bson) if not attr.startswith('_')]
    for attr in sorted(attrs):
        print(f"    - {attr}")
except ImportError as e:
    print(f"✗ Failed to import bson: {e}")
    sys.exit(1)

# Check pymongo
try:
    import pymongo
    print(f"\n✓ pymongo found: {pymongo.__file__}")
    print(f"  Version: {pymongo.__version__}")
except ImportError as e:
    print(f"\n✗ Failed to import pymongo: {e}")

# Check if decode_all exists
print("\n" + "=" * 60)
print("Checking decode functions:")
print("=" * 60)

functions_to_check = ['decode', 'decode_all', 'decode_iter', 'BSON', 'encode']
for func_name in functions_to_check:
    if hasattr(bson, func_name):
        print(f"✓ bson.{func_name} exists")
    else:
        print(f"✗ bson.{func_name} NOT FOUND")

# Try to decode a simple BSON document
print("\n" + "=" * 60)
print("Testing BSON decode:")
print("=" * 60)

try:
    # Create a simple BSON document
    from bson import encode
    test_doc = {"test": "hello", "number": 123}
    encoded = encode(test_doc)
    print(f"✓ Encoded test document: {len(encoded)} bytes")
    
    # Try different decode methods
    if hasattr(bson, 'decode'):
        decoded = bson.decode(encoded)
        print(f"✓ bson.decode() works: {decoded}")
    elif hasattr(bson, 'decode_all'):
        decoded = bson.decode_all(encoded)
        print(f"✓ bson.decode_all() works: {decoded}")
    else:
        print("✗ No decode method available!")
        
except Exception as e:
    print(f"✗ Test failed: {e}")

print("\n" + "=" * 60)
