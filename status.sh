#!/bin/bash

# Gateway Service Status Check Script
# This script checks the status of all Gateway Service components

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
print_running() {
    echo -e "  ${GREEN}●${NC} $1 ${GREEN}[RUNNING]${NC}"
}

print_stopped() {
    echo -e "  ${RED}●${NC} $1 ${RED}[STOPPED]${NC}"
}

print_warning() {
    echo -e "  ${YELLOW}●${NC} $1 ${YELLOW}[WARNING]${NC}"
}

print_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# Main status check
print_header "📊 Gateway Service Status"

# Check FastAPI service
echo -e "${BLUE}Gateway Service:${NC}"
if [ -f ".uvicorn.pid" ]; then
    UVICORN_PID=$(cat .uvicorn.pid)
    if ps -p $UVICORN_PID > /dev/null 2>&1; then
        print_running "Uvicorn (PID: $UVICORN_PID)"
        
        # Check if port 8000 is listening
        if lsof -ti:8000 > /dev/null 2>&1; then
            echo -e "    ${GREEN}→${NC} Listening on port 8000"
        else
            print_warning "Port 8000 not listening"
        fi
    else
        print_stopped "Uvicorn (stale PID file)"
    fi
else
    # Check if something is running on port 8000
    PID=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$PID" ]; then
        print_running "Uvicorn (PID: $PID) - no PID file"
    else
        print_stopped "Uvicorn"
    fi
fi

# Check health endpoint
echo -e "\n${BLUE}Service Health:${NC}"
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health 2>/dev/null)
if [ "$HEALTH_CHECK" = "200" ]; then
    print_running "Health endpoint responding (HTTP 200)"
else
    print_stopped "Health endpoint not responding"
fi

# Check Docker containers
echo -e "\n${BLUE}Docker Containers:${NC}"
POSTGRES_STATUS=$(docker-compose ps -q postgres 2>/dev/null)
if [ ! -z "$POSTGRES_STATUS" ] && [ "$(docker inspect -f '{{.State.Running}}' $(docker-compose ps -q postgres 2>/dev/null) 2>/dev/null)" = "true" ]; then
    print_running "PostgreSQL"
    # Check if PostgreSQL is accepting connections
    if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
        echo -e "    ${GREEN}→${NC} Accepting connections"
    else
        print_warning "Not accepting connections"
    fi
else
    print_stopped "PostgreSQL"
fi

REDIS_STATUS=$(docker-compose ps -q redis 2>/dev/null)
if [ ! -z "$REDIS_STATUS" ] && [ "$(docker inspect -f '{{.State.Running}}' $(docker-compose ps -q redis 2>/dev/null) 2>/dev/null)" = "true" ]; then
    print_running "Redis"
else
    print_stopped "Redis"
fi

# Check virtual environment
echo -e "\n${BLUE}Virtual Environment:${NC}"
if [ -d "venv" ]; then
    print_running "Virtual environment exists"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo -e "    ${GREEN}→${NC} Currently activated"
    else
        echo -e "    ${YELLOW}→${NC} Not activated in current shell"
    fi
else
    print_stopped "Virtual environment not found"
fi

# Display service URLs if running
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}Service URLs:${NC}"
    echo -e "  ${BLUE}➜${NC}  API:        http://localhost:8000"
    echo -e "  ${BLUE}➜${NC}  Swagger UI: http://localhost:8000/docs"
    echo -e "  ${BLUE}➜${NC}  ReDoc:      http://localhost:8000/redoc"
    echo -e "  ${BLUE}➜${NC}  Health:     http://localhost:8000/api/v1/health"
    echo -e ""
    echo -e "${YELLOW}📝 Note: This localhost refers to the computer running this service,${NC}"
    echo -e "${YELLOW}   not your local machine. To access remotely, deploy on your system.${NC}"
fi

# Display management commands
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Management Commands:${NC}"
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "  ${BLUE}➜${NC}  Stop:    ./stop.sh"
    echo -e "  ${BLUE}➜${NC}  Restart: ./restart.sh"
    echo -e "  ${BLUE}➜${NC}  Logs:    tail -f uvicorn.log"
else
    echo -e "  ${BLUE}➜${NC}  Start:   ./start.sh"
fi
echo -e ""
