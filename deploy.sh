#!/bin/bash
set -e

echo "🚀 Supreme Cycle Store - Production Deployment"
echo "==============================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running on EC2
print_step "🔍 Checking environment..."
if [[ ! -f /sys/hypervisor/uuid ]] || [[ ! $(head -3 /sys/hypervisor/uuid 2>/dev/null | grep -i ec2) ]]; then
    print_warning "This doesn't appear to be an AWS EC2 instance"
fi

# Check prerequisites
print_step "📋 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sudo sh get-docker.sh"
    echo "  sudo usermod -aG docker \$USER"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install it first:"
    echo "  sudo curl -L \"https://github.com/docker/compose/releases/download/v2.24.0/docker compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker compose"
    echo "  sudo chmod +x /usr/local/bin/docker compose"
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Check if ports are available
if sudo netstat -tlnp 2>/dev/null | grep -E ':(80|443)' | grep -v docker; then
    print_warning "Ports 80 or 443 are in use by other services"
    echo "You may need to stop other web servers:"
    echo "  sudo systemctl stop nginx apache2 2>/dev/null || true"
fi

# Build and start the application
print_step "🔨 Building and starting the application..."

# Create necessary directories
mkdir -p logs data ssl

# Pull latest images and rebuild
docker compose pull
docker compose build --no-cache

# Start services
docker compose up -d

# Wait for services to start
print_step "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker compose ps | grep -q "Up"; then
    print_success "Services are running successfully!"
    
    echo ""
    echo "🌐 Your application is now available at:"
    echo "   • http://$(curl -s ifconfig.me 2>/dev/null || echo 'YOUR-IP')"
    echo "   • http://localhost (if accessing locally)"
    echo ""
    
    # Get public IP for domain setup instructions
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "YOUR-EC2-IP")
    echo "📝 To connect your domain supremecycle.in:"
    echo "   1. Go to GoDaddy DNS management"
    echo "   2. Add A record: @ → $PUBLIC_IP"
    echo "   3. Add A record: www → $PUBLIC_IP"
    echo "   4. Wait 5-60 minutes for DNS propagation"
    echo "   5. Run: ./setup_ssl.sh (for HTTPS)"
    echo ""
    
    print_step "🔍 Health check..."
    if curl -f -s http://localhost/health > /dev/null; then
        print_success "Application health check passed"
    else
        print_warning "Application might still be starting up"
        echo "Check logs with: docker compose logs"
    fi
    
    echo ""
    echo "📊 Useful commands:"
    echo "   • View logs: docker compose logs -f"
    echo "   • Restart: docker compose restart"
    echo "   • Stop: docker compose down"
    echo "   • Setup SSL: ./setup_ssl.sh"
    echo ""
    
else
    print_error "Some services failed to start"
    echo "Check the logs for more details:"
    echo "  docker compose logs"
    exit 1
fi

print_success "Deployment completed! 🎉"
