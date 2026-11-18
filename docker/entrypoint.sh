#!/bin/bash
# Docker container entrypoint — RAKSHA-NET
# Sets up IP forwarding and static routes for each node role.
# Usage: entrypoint.sh [A|GW|LEO1|LEO2|B] [additional args...]

set -e
NODE=$1
shift

echo "[entrypoint] Node: $NODE"

# Enable IP forwarding (already set via sysctl in compose)

# Configure static routes for each node
case $NODE in
  A)
    # Route to B via GW (both paths — GW decides which LEO to use)
    ip route add 10.10.4.0/24 via 10.10.1.3 2>/dev/null || true
    ip route add 10.10.5.0/24 via 10.10.1.3 2>/dev/null || true
    # Route UE traffic back to Open5GS UPF (for 5G integration)
    UPF_IP=10.10.9.1
    UE_SUBNET=10.45.0.0/16
    ip route add $UE_SUBNET via $UPF_IP dev eth1 2>/dev/null || true
    ;;
  GW)
    # Route to B via LEO-1 by default; controller switches to LEO-2
    ip route add 10.10.4.0/24 via 10.10.2.3 2>/dev/null || true  # LEO-1 path
    ip route add 10.10.5.0/24 via 10.10.3.3 2>/dev/null || true  # LEO-2 path
    ;;
  LEO1)
    ip route add 10.10.1.0/24 via 10.10.2.2 2>/dev/null || true  # back to GW
    ip route add 10.10.5.0/24 via 10.10.2.2 2>/dev/null || true  # to B LEO2 side
    ;;
  LEO2)
    ip route add 10.10.1.0/24 via 10.10.3.2 2>/dev/null || true  # back to GW
    ip route add 10.10.4.0/24 via 10.10.3.2 2>/dev/null || true  # to B LEO1 side
    ;;
  B)
    # Node B has two interfaces: leo1_b and leo2_b
    ip route add 10.10.1.0/24 via 10.10.4.2 2>/dev/null || true  # via LEO-1
    ;;
esac

echo "[entrypoint] Routes configured for $NODE"
ip route show

# Start the application
exec python -m scripts.node_stub "$NODE" "$@"
