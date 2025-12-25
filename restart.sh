#!/bin/bash

# Gateway Service Restart Script
# This script stops and then starts the Gateway Service

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Main restart sequence
print_header "🔄 Restarting Gateway Service"

# Step 1: Stop the service
print_info "Stopping Gateway Service..."
./stop.sh
if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Stop script encountered issues${NC}"
fi

# Step 2: Wait a moment
print_info "Waiting 3 seconds..."
sleep 3

# Step 3: Start the service
print_info "Starting Gateway Service..."
./start.sh

exit $?
