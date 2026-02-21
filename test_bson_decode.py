#!/usr/bin/env python
"""Test BSON decoding with new method"""

import os
import bson

# Test with users.bson file
test_file = 'backup_data/users.bson'

if not os.path.exists(test_file):
    print(f"✗ Test file not found: {test_file}")
    exit(1)

print(f"Testing BSON decode with: {test_file}")
print("=" * 60)

try:
    with open(test_file, 'rb') as f:
        raw_data = f.read()
    
    print(f"✓ Read {len(raw_data)} bytes")
    
    # Try Method 1: decode_all
    print("\n[Method 1] Trying bson.decode_all()...")
    try:
        from bson import decode_all
        data = decode_all(raw_data)
        print(f"✓ SUCCESS! Decoded {len(data)} documents")
        print(f"  First document keys: {list(data[0].keys())}")
    except (ImportError, AttributeError) as e:
        print(f"  ✗ Failed: {e}")
        print("\n[Method 2] Trying manual parsing...")
        
        # Try Method 2: Manual parsing
        data = []
        offset = 0
        while offset < len(raw_data):
            if offset + 4 > len(raw_data):
                break
            doc_size = int.from_bytes(raw_data[offset:offset+4], 'little')
            if offset + doc_size > len(raw_data):
                break
            
            doc_bytes = raw_data[offset:offset+doc_size]
            
            # Try different decode methods
            decoded = False
            
            # Try BSON class
            if hasattr(bson, 'BSON'):
                try:
                    doc = bson.BSON(doc_bytes).decode()
                    data.append(doc)
                    decoded = True
                except Exception as e:
                    print(f"  BSON class failed: {e}")
            
            # Try decode function
            if not decoded and hasattr(bson, 'decode'):
                try:
                    doc = bson.decode(doc_bytes)
                    data.append(doc)
                    decoded = True
                except Exception as e:
                    print(f"  decode() failed: {e}")
            
            # Try codec directly
            if not decoded:
                try:
                    from bson.codec_options import CodecOptions
                    codec_opts = CodecOptions()
                    doc = bson._bson_to_dict(doc_bytes, codec_opts)[0]
                    data.append(doc)
                    decoded = True
                except Exception as e:
                    print(f"  codec failed: {e}")
            
            if not decoded:
                print(f"  ✗ Failed to decode document at offset {offset}")
                break
            
            offset += doc_size
        
        if data:
            print(f"✓ SUCCESS! Decoded {len(data)} documents")
            print(f"  First document keys: {list(data[0].keys())}")
        else:
            print(f"✗ FAILED to decode any documents")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
