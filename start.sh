#!/bin/bash

# Gateway Service Startup Script
# This script handles all setup and startup tasks for the Gateway Service

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

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for database to be ready
wait_for_db() {
    print_info "Waiting for PostgreSQL to be ready..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
            print_success "PostgreSQL is ready!"
            return 0
        fi
        echo -n "."
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "PostgreSQL failed to start after ${max_attempts} seconds"
    return 1
}

# Main startup sequence
print_header "🚀 Starting Gateway Service"

# Step 1: Check for required commands
print_info "Checking for required commands..."
if ! command_exists python3; then
    print_error "python3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

if ! command_exists docker; then
    print_error "docker is not installed. Please install Docker."
    exit 1
fi

if ! command_exists docker-compose; then
    print_error "docker-compose is not installed. Please install Docker Compose."
    exit 1
fi
print_success "All required commands are available"

# Step 2: Check/Create .env file
print_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_warning ".env file not found. Copying from .env.example..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please review and update .env file with your configuration"
    else
        print_error ".env.example not found. Cannot create .env file."
        exit 1
    fi
else
    print_success ".env file exists"
fi

# Step 3: Set up virtual environment
print_info "Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        print_success "Virtual environment created"
    else
        print_error "Failed to create virtual environment"
        exit 1
    fi
else
    print_success "Virtual environment already exists"
fi

# Step 4: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    print_success "Virtual environment activated"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# Step 5: Install/Update dependencies
print_info "Installing/Updating dependencies..."
pip install --upgrade pip >/dev/null 2>&1
pip install -r requirements.txt >/dev/null 2>&1
if [ $? -eq 0 ]; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Step 6: Start Docker containers
print_info "Starting Docker containers (PostgreSQL, Redis)..."
docker-compose up -d
if [ $? -eq 0 ]; then
    print_success "Docker containers started"
else
    print_error "Failed to start Docker containers"
    exit 1
fi

# Step 7: Wait for database to be ready
if ! wait_for_db; then
    print_error "Database is not ready. Startup failed."
    exit 1
fi

# Step 8: Run database migrations
print_info "Running database migrations..."
alembic upgrade head
if [ $? -eq 0 ]; then
    print_success "Database migrations completed"
else
    print_error "Failed to run database migrations"
    exit 1
fi

# Step 9: Start FastAPI service
print_info "Starting Gateway Service on port 8000..."

# Kill any existing uvicorn process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start uvicorn in the background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > uvicorn.log 2>&1 &
UVICORN_PID=$!

# Wait a moment for the service to start
sleep 3

# Check if the service is running
if ps -p $UVICORN_PID > /dev/null; then
    print_success "Gateway Service started (PID: $UVICORN_PID)"
    echo $UVICORN_PID > .uvicorn.pid
else
    print_error "Failed to start Gateway Service"
    exit 1
fi

# Final success message
print_header "✅ Gateway Service Started Successfully!"

echo -e "${GREEN}Service is running at:${NC}"
echo -e "  ${BLUE}➜${NC}  Local:   http://localhost:8000"
echo -e "  ${BLUE}➜${NC}  Network: http://0.0.0.0:8000"
echo -e ""
echo -e "${GREEN}API Documentation:${NC}"
echo -e "  ${BLUE}➜${NC}  Swagger UI: http://localhost:8000/docs"
echo -e "  ${BLUE}➜${NC}  ReDoc:      http://localhost:8000/redoc"
echo -e ""
echo -e "${YELLOW}📝 Note: This localhost refers to the computer running this service,${NC}"
echo -e "${YELLOW}   not your local machine. To access remotely, deploy on your system.${NC}"
echo -e ""
echo -e "${GREEN}Logs:${NC}"
echo -e "  ${BLUE}➜${NC}  tail -f uvicorn.log"
echo -e ""
echo -e "${GREEN}Management:${NC}"
echo -e "  ${BLUE}➜${NC}  Stop:    ./stop.sh"
echo -e "  ${BLUE}➜${NC}  Restart: ./restart.sh"
echo -e "  ${BLUE}➜${NC}  Status:  ./status.sh"
echo -e ""
