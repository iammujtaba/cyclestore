#!/bin/bash

echo "Setting up SSL with Let's Encrypt for supremecycle.in"
echo "======================================================"

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Update system packages
echo "1. Updating system packages..."
$SUDO apt update

# Install snapd if not already installed
echo "2. Installing snapd..."
$SUDO apt install snapd -y

# Install certbot via snap
echo "3. Installing Certbot..."
$SUDO snap install core; $SUDO snap refresh core
$SUDO snap install --classic certbot

# Create symlink for certbot command
$SUDO ln -sf /snap/bin/certbot /usr/bin/certbot

# Create SSL directory for docker
echo "4. Creating SSL directory..."
mkdir -p ./ssl

# Stop nginx temporarily for certificate generation
echo "5. Stopping nginx for certificate generation..."
docker-compose down

# Generate SSL certificates
echo "6. Generating SSL certificates..."
echo "You'll be prompted to enter an email and agree to terms."
echo "Make sure your domain supremecycle.in is pointing to this IP: 13.201.4.201"
echo ""
read -p "Press Enter to continue..."

$SUDO certbot certonly --standalone \
  --email admin@supremecycle.in \
  --agree-tos \
  --no-eff-email \
  -d supremecycle.in \
  -d www.supremecycle.in

# Check if certificates were generated successfully
if [ -f "/etc/letsencrypt/live/supremecycle.in/fullchain.pem" ]; then
    echo "✓ SSL certificates generated successfully!"
    
    # Copy certificates to project directory
    echo "7. Copying certificates to project directory..."
    $SUDO cp /etc/letsencrypt/live/supremecycle.in/fullchain.pem ./ssl/cert.pem
    $SUDO cp /etc/letsencrypt/live/supremecycle.in/privkey.pem ./ssl/key.pem
    $SUDO chmod 644 ./ssl/cert.pem
    $SUDO chmod 600 ./ssl/key.pem
    $SUDO chown $USER:$USER ./ssl/*
    
    echo "✓ Certificates copied to ./ssl/ directory"
    
    # Set up auto-renewal script
    echo "8. Setting up auto-renewal..."
    cat > renew_ssl.sh << 'EOF'
#!/bin/bash
sudo certbot renew --quiet
if [ $? -eq 0 ]; then
    sudo cp /etc/letsencrypt/live/supremecycle.in/fullchain.pem ./ssl/cert.pem
    sudo cp /etc/letsencrypt/live/supremecycle.in/privkey.pem ./ssl/key.pem
    sudo chmod 644 ./ssl/cert.pem
    sudo chmod 600 ./ssl/key.pem
    sudo chown $USER:$USER ./ssl/*
    docker-compose restart nginx
    echo "SSL certificates renewed and nginx restarted"
fi
EOF
    chmod +x renew_ssl.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "0 3 * * * cd $(pwd) && ./renew_ssl.sh >> ./logs/ssl_renewal.log 2>&1") | crontab -
    
    echo "✓ Auto-renewal cron job added"
    echo ""
    echo "9. Starting services with HTTPS enabled..."
    docker-compose up -d
    
    echo ""
    echo "🎉 SSL setup completed successfully!"
    echo ""
    echo "Your website is now available at:"
    echo "- https://supremecycle.in"
    echo "- https://www.supremecycle.in"
    echo ""
    echo "HTTP traffic will automatically redirect to HTTPS"
    echo ""
    echo "Next steps:"
    echo "1. Test HTTPS access: curl -I https://supremecycle.in"
    echo "2. Check SSL grade: https://www.ssllabs.com/ssltest/"
    echo "3. Verify auto-renewal: sudo certbot renew --dry-run"
    
else
    echo "✗ Failed to generate SSL certificates"
    echo ""
    echo "Please check:"
    echo "1. Domain supremecycle.in points to this IP (13.201.4.201)"
    echo "2. Port 80 is open in AWS security group"
    echo "3. No other service is using port 80"
    echo "4. DNS has propagated (wait 5-60 minutes after DNS update)"
    echo ""
    echo "Debug commands:"
    echo "- Check DNS: dig A supremecycle.in"
    echo "- Check port 80: sudo netstat -tlnp | grep :80"
    echo "- Test connectivity: curl -I http://supremecycle.in"
fi
