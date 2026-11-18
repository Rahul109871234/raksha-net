#!/bin/bash
# UE traffic generator — RAKSHA-NET
# Generates UDP/TCP traffic from UE side toward Node B via the RAKSHA gateway.
# Usage: bash scripts/ue_traffic.sh [UE_IP] [NODE_B_IP] [duration_s]
#
# If iperf3 is not available on UE, you can run from Node A container:
#   docker exec node_a bash scripts/ue_traffic.sh

set -e

UE_IP="${1:-10.45.0.2}"            # UE IP from Open5GS pool
NODE_B_IP="${2:-10.10.4.3}"        # Node B IP (LEO-1 path)
DURATION="${3:-60}"                  # seconds

echo "RAKSHA-NET UE Traffic Generator"
echo "UE: $UE_IP | Destination: $NODE_B_IP | Duration: ${DURATION}s"
echo "---"

# Check iperf3 is available
if ! command -v iperf3 &>/dev/null; then
    echo "ERROR: iperf3 not found. Install with: apt-get install iperf3"
    exit 1
fi

# Ensure iperf3 server is running on Node B
echo "Starting iperf3 server on Node B (if reachable)..."
# Try to start server remotely (docker exec) if on the same host
docker exec -d node_b iperf3 -s 2>/dev/null || echo "(Note: Start iperf3 -s on Node B manually if needed)"
sleep 1

# UDP test (10 Mbps for the duration)
echo ""
echo "[1/2] UDP throughput test (10 Mbps, ${DURATION}s)..."
iperf3 -c "$NODE_B_IP" -u -b 10M -t "$DURATION" --bind "$UE_IP" 2>&1 || \
    iperf3 -c "$NODE_B_IP" -u -b 10M -t "$DURATION" 2>&1

# TCP test
echo ""
echo "[2/2] TCP throughput test (${DURATION}s)..."
iperf3 -c "$NODE_B_IP" -t "$DURATION" 2>&1

echo ""
echo "UE traffic test complete."
