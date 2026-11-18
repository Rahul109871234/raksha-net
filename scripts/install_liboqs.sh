#!/bin/bash
# liboqs installation script for Ubuntu/WSL2 — RAKSHA-NET
# Installs liboqs C library + liboqs-python for ML-KEM-768 and ML-DSA support.
#
# Prerequisites: Ubuntu 22.04+ or WSL2 with Ubuntu
# Run as: bash scripts/install_liboqs.sh
#
# After installation, re-run the scenario to get BACKEND=liboqs-ML-KEM-768.

set -e

echo "=================================================="
echo "RAKSHA-NET: liboqs-python installation"
echo "Ubuntu 22.04+ / WSL2 required"
echo "=================================================="
echo ""

# Check OS
if ! grep -qi ubuntu /etc/os-release 2>/dev/null; then
    echo "WARNING: This script is designed for Ubuntu. Proceed with caution."
fi

# System dependencies
echo "[1/4] Installing system dependencies..."
sudo apt-get update -q
sudo apt-get install -y --no-install-recommends \
    cmake ninja-build pkg-config \
    libssl-dev python3-dev python3-pip \
    build-essential git

# Clone and build liboqs
LIBOQS_DIR="/tmp/liboqs-build"
echo ""
echo "[2/4] Building liboqs C library..."
if [ ! -d "$LIBOQS_DIR" ]; then
    git clone --depth 1 https://github.com/open-quantum-safe/liboqs.git "$LIBOQS_DIR"
fi
mkdir -p "$LIBOQS_DIR/build"
cd "$LIBOQS_DIR/build"
cmake -GNinja -DOQS_USE_OPENSSL=ON -DCMAKE_BUILD_TYPE=Release ..
ninja
sudo ninja install
sudo ldconfig

echo ""
echo "[3/4] Installing liboqs-python..."
pip install liboqs-python

# Verify
echo ""
echo "[4/4] Verifying installation..."
python3 -c "
import oqs
print('  ML-KEM-768: OK')
with oqs.KeyEncapsulation('ML-KEM-768') as kem:
    pk = kem.generate_keypair()
    with oqs.KeyEncapsulation('ML-KEM-768') as srv:
        ct, ss_srv = srv.encap_secret(pk)
    ss_cli = kem.decap_secret(ct)
    assert ss_cli == ss_srv
    print(f'  KEM round-trip: PASS (ss={ss_cli[:8].hex()}...)')

# Try ML-DSA
for alg in ['ML-DSA-65', 'Dilithium3']:
    try:
        with oqs.Signature(alg) as sig:
            pk = sig.generate_keypair()
        print(f'  {alg}: OK')
        break
    except Exception:
        pass
"

echo ""
echo "=================================================="
echo "Installation complete!"
echo "Restart the RAKSHA controller to use ML-KEM-768."
echo "BACKEND will change from MOCK to liboqs-ML-KEM-768."
echo "=================================================="
