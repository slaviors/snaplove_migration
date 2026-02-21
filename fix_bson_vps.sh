#!/bin/bash
# Fix BSON decoding issues on VPS

echo "============================================================"
echo "Fixing BSON Package Conflicts"
echo "============================================================"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Check current packages
echo ""
echo "[Step 1] Checking installed packages..."
pip list | grep -E "(bson|pymongo)"

# Uninstall conflicting bson package
echo ""
echo "[Step 2] Removing standalone 'bson' package if exists..."
pip uninstall bson -y 2>/dev/null || echo "  (bson not installed or already removed)"

# Reinstall pymongo to ensure clean installation
echo ""
echo "[Step 3] Reinstalling pymongo..."
pip install --force-reinstall --no-cache-dir pymongo==4.6.0

# Verify installation
echo ""
echo "[Step 4] Verifying installation..."
python3 << EOF
import sys
try:
    import pymongo
    import bson
    from bson import decode_all
    print(f"✓ pymongo version: {pymongo.__version__}")
    print(f"✓ bson module: {bson.__file__}")
    print(f"✓ bson.decode_all exists: {hasattr(bson, 'decode_all')}")
    print("\n✓ All checks passed!")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "============================================================"
    echo "✓ Fix completed successfully!"
    echo "============================================================"
    echo ""
    echo "You can now run: python converter.py"
else
    echo ""
    echo "============================================================"
    echo "✗ Fix failed - please check errors above"
    echo "============================================================"
    exit 1
fi
