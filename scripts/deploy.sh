#!/bin/bash

# Telegram Job Scraper Deployment Script
# This script provides easy deployment and management options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="telegram-job-scraper"
DOCKER_IMAGE="telegram-job-scraper"
COMPOSE_FILE="docker-compose.yml"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        log_warning ".env file not found. Creating from template..."
        if [ -f "config_template.txt" ]; then
            cp config_template.txt .env
            log_warning "Please edit .env file with your configuration before deploying."
        else
            log_error "No .env file or config template found. Please create .env file manually."
            exit 1
        fi
    fi
    
    log_success "Dependencies check passed"
}

create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p data logs sessions config ssl
    
    # Set proper permissions
    chmod 755 data logs sessions config
    chmod 700 ssl
    
    log_success "Directories created"
}

build_image() {
    log_info "Building Docker image..."
    
    docker build -t $DOCKER_IMAGE .
    
    if [ $? -eq 0 ]; then
        log_success "Docker image built successfully"
    else
        log_error "Failed to build Docker image"
        exit 1
    fi
}

deploy() {
    local mode=${1:-production}
    
    log_info "Deploying in $mode mode..."
    
    case $mode in
        "production")
            docker-compose -f $COMPOSE_FILE up -d --build
            ;;
        "development")
            docker-compose -f $COMPOSE_FILE --profile development up -d --build
            ;;
        *)
            log_error "Invalid mode: $mode. Use 'production' or 'development'"
            exit 1
            ;;
    esac
    
    log_success "Deployment completed"
}

stop() {
    log_info "Stopping services..."
    
    docker-compose -f $COMPOSE_FILE down
    
    log_success "Services stopped"
}

restart() {
    log_info "Restarting services..."
    
    docker-compose -f $COMPOSE_FILE restart
    
    log_success "Services restarted"
}

logs() {
    local service=${1:-telegram-scraper}
    local lines=${2:-100}
    
    log_info "Showing logs for $service (last $lines lines)..."
    
    docker-compose -f $COMPOSE_FILE logs -f --tail=$lines $service
}

status() {
    log_info "Checking service status..."
    
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "Health check status:"
    docker-compose -f $COMPOSE_FILE exec telegram-scraper curl -f http://localhost:5000/health 2>/dev/null || log_warning "Health check failed"
}

backup() {
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    
    log_info "Creating backup in $backup_dir..."
    
    mkdir -p $backup_dir
    
    # Backup database
    if [ -f "data/jobs.db" ]; then
        cp data/jobs.db $backup_dir/
        log_info "Database backed up"
    fi
    
    # Backup logs
    if [ -d "logs" ]; then
        cp -r logs $backup_dir/
        log_info "Logs backed up"
    fi
    
    # Backup configuration
    if [ -f ".env" ]; then
        cp .env $backup_dir/
        log_info "Configuration backed up"
    fi
    
    log_success "Backup completed: $backup_dir"
}

update() {
    log_info "Updating application..."
    
    # Pull latest changes
    git pull origin main
    
    # Rebuild and restart
    build_image
    restart
    
    log_success "Update completed"
}

cleanup() {
    log_warning "This will remove all containers, images, and data. Are you sure? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        log_info "Cleaning up..."
        
        # Stop and remove containers
        docker-compose -f $COMPOSE_FILE down -v
        
        # Remove images
        docker rmi $DOCKER_IMAGE 2>/dev/null || true
        
        # Remove data (optional)
        log_warning "Remove all data? This cannot be undone. (y/N)"
        read -r data_response
        
        if [[ "$data_response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            rm -rf data logs sessions
            log_info "Data removed"
        fi
        
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

show_help() {
    echo "Telegram Job Scraper Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  deploy [mode]     Deploy the application (production|development)"
    echo "  stop              Stop all services"
    echo "  restart           Restart all services"
    echo "  logs [service]    Show logs for a service"
    echo "  status            Show service status"
    echo "  backup            Create a backup of data and configuration"
    echo "  update            Update the application"
    echo "  cleanup           Remove all containers and data"
    echo "  help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy production"
    echo "  $0 deploy development"
    echo "  $0 logs telegram-scraper"
    echo "  $0 status"
}

# Main script
case "${1:-help}" in
    "deploy")
        check_dependencies
        create_directories
        build_image
        deploy "${2:-production}"
        ;;
    "stop")
        stop
        ;;
    "restart")
        restart
        ;;
    "logs")
        logs "$2" "$3"
        ;;
    "status")
        status
        ;;
    "backup")
        backup
        ;;
    "update")
        update
        ;;
    "cleanup")
        cleanup
        ;;
    "help"|"--help"|"-h")
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 