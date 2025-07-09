#!/bin/bash
set -e

echo "🔐 Setting up SSL with Let's Encrypt for supremecycle.in"
echo "========================================================="

# Check prerequisites
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is required but not installed."
    exit 1
fi

# Create SSL directory
mkdir -p ./ssl

echo "📋 Prerequisites checklist:"
echo "1. ✅ Domain supremecycle.in points to this server IP"
echo "2. ✅ Port 80 and 443 are open in AWS security group"
echo "3. ✅ No other services using ports 80/443"
echo ""

read -p "Continue with SSL setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "SSL setup cancelled."
    exit 0
fi

# Stop containers for certificate generation
echo "🛑 Stopping containers..."
docker-compose down

# Install Certbot
echo "📦 Installing Certbot..."
sudo apt update -qq
sudo apt install -y snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -sf /snap/bin/certbot /usr/bin/certbot

# Generate certificates
echo "🔐 Generating SSL certificates..."
sudo certbot certonly --standalone \
  --email admin@supremecycle.in \
  --agree-tos \
  --no-eff-email \
  -d supremecycle.in \
  -d www.supremecycle.in

# Copy certificates to project
if [ -f "/etc/letsencrypt/live/supremecycle.in/fullchain.pem" ]; then
    echo "📋 Copying certificates..."
    sudo cp /etc/letsencrypt/live/supremecycle.in/fullchain.pem ./ssl/cert.pem
    sudo cp /etc/letsencrypt/live/supremecycle.in/privkey.pem ./ssl/key.pem
    sudo chmod 644 ./ssl/cert.pem
    sudo chmod 600 ./ssl/key.pem
    sudo chown $USER:$USER ./ssl/*
    
    # Setup auto-renewal
    echo "🔄 Setting up auto-renewal..."
    (crontab -l 2>/dev/null; echo "0 3 * * * cd $(pwd) && sudo certbot renew --quiet && sudo cp /etc/letsencrypt/live/supremecycle.in/*.pem ./ssl/ && docker-compose restart nginx") | crontab -
    
    # Start services with SSL
    echo "🚀 Starting services with HTTPS..."
    docker compose up
    
    echo ""
    echo "🎉 SSL setup completed successfully!"
    echo ""
    echo "✅ Your website is now available at:"
    echo "   • https://supremecycle.in"
    echo "   • https://www.supremecycle.in"
    echo ""
    echo "📊 Test your SSL setup:"
    echo "   curl -I https://supremecycle.in"
    echo "   SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=supremecycle.in"
    
else
    echo "❌ SSL certificate generation failed!"
    echo ""
    echo "🔍 Troubleshooting steps:"
    echo "1. Verify DNS: dig A supremecycle.in"
    echo "2. Check connectivity: curl -I http://supremecycle.in"
    echo "3. Ensure ports 80/443 are open"
    echo "4. Wait for DNS propagation (5-60 minutes)"
    
    # Restart without SSL
    docker compose up -d
    exit 1
fi
