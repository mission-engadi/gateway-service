#!/bin/bash

# Gateway Service Shutdown Script
# This script gracefully stops all Gateway Service components

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
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Main shutdown sequence
print_header "🛑 Stopping Gateway Service"

# Step 1: Stop FastAPI service
print_info "Stopping Gateway Service..."
if [ -f ".uvicorn.pid" ]; then
    UVICORN_PID=$(cat .uvicorn.pid)
    if ps -p $UVICORN_PID > /dev/null 2>&1; then
        kill $UVICORN_PID
        sleep 2
        # Force kill if still running
        if ps -p $UVICORN_PID > /dev/null 2>&1; then
            kill -9 $UVICORN_PID
        fi
        rm -f .uvicorn.pid
        print_success "Gateway Service stopped"
    else
        print_warning "Gateway Service was not running (PID not found)"
        rm -f .uvicorn.pid
    fi
else
    # Try to kill by port
    PID=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$PID" ]; then
        kill $PID
        sleep 2
        # Force kill if still running
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID
        fi
        print_success "Gateway Service stopped"
    else
        print_warning "Gateway Service was not running"
    fi
fi

# Step 2: Stop Docker containers
print_info "Stopping Docker containers..."
docker-compose down
if [ $? -eq 0 ]; then
    print_success "Docker containers stopped"
else
    print_warning "Failed to stop Docker containers (they may not be running)"
fi

# Step 3: Deactivate virtual environment (if active)
if [ -n "$VIRTUAL_ENV" ]; then
    print_info "Deactivating virtual environment..."
    deactivate 2>/dev/null || true
    print_success "Virtual environment deactivated"
fi

# Final message
print_header "✅ Gateway Service Stopped"

echo -e "${GREEN}All services have been stopped successfully.${NC}"
echo -e ""
echo -e "${GREEN}To start again:${NC}"
echo -e "  ${BLUE}➜${NC}  ./start.sh"
echo -e ""
