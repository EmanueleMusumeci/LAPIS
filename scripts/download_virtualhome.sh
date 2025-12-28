#!/bin/bash

# Exit on error
set -e

# Define paths
VH_ROOT="third-party/virtualhome"
SIM_DIR="$VH_ROOT/simulation/unity_simulator"
URL="http://virtual-home.org//release/simulator/v2.0/v2.3.0/linux_exec.zip"

echo "Setting up VirtualHome Unity Simulator..."

# Create directory
mkdir -p "$SIM_DIR"

# Download
echo "Downloading simulator from $URL..."
wget -O "$SIM_DIR/linux_exec.zip" "$URL"

# Extract
echo "Extracting..."
unzip -o "$SIM_DIR/linux_exec.zip" -d "$SIM_DIR"

# Cleanup
rm "$SIM_DIR/linux_exec.zip"

# Make executable
chmod +x "$SIM_DIR/linux_exec.v2.3.0.x86_64"

echo "Done! Simulator installed in $SIM_DIR"
echo "To run (with graphics): $SIM_DIR/linux_exec.v2.3.0.x86_64"
echo "To run (headless): xvfb-run --auto-servernum --server-args='-screen 0 640x480x24' $SIM_DIR/linux_exec.v2.3.0.x86_64 -batchmode -http-port 8080"
