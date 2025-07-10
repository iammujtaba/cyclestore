#!/bin/bash
set -e

echo "🔐 SSL Certificate Setup"
echo "========================"
echo "1. Self-signed certificates (development/testing)"
echo "2. Let's Encrypt certificates (production)"
echo ""

read -p "Choose option (1 or 2): " -n 1 -r
echo

if [[ $REPLY == "1" ]]; then
    echo "🔧 Creating self-signed certificates..."
    
    # Create SSL directory
    mkdir -p ./ssl
    
    # Generate self-signed certificate
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ./ssl/key.pem \
        -out ./ssl/cert.pem \
        -subj "/C=IN/ST=Karnataka/L=Bangalore/O=CycleStore/CN=localhost"
    
    # Create nginx SSL configuration
    echo "📝 Creating nginx SSL configuration..."
    mkdir -p ./nginx-conf.d
    cat > ./nginx-conf.d/ssl.conf << 'EOF'
# HTTPS server configuration - automatically included when SSL certificates exist
server {
    listen 443 ssl;
    server_name supremecycle.in www.supremecycle.in;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /static/ {
        alias /var/www/static/;
    }
}
EOF

    # Restart services with SSL
    echo "🚀 Restarting services with HTTPS..."
    docker compose restart nginx
    
    echo ""
    echo "🎉 Self-signed SSL setup completed!"
    echo ""
    echo "✅ Your website is now available at:"
    echo "   • https://localhost (⚠️  You'll see a security warning - click 'Advanced' and 'Proceed')"
    echo "   • http://localhost (still works)"
    echo ""
    
elif [[ $REPLY == "2" ]]; then
    echo "🔐 Setting up Let's Encrypt certificates for production..."
    echo ""

    # Check prerequisites
    if ! command -v docker compose &> /dev/null; then
        echo "❌ docker compose is required but not installed."
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
    docker compose down

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
        
        # Create nginx SSL configuration
        echo "📝 Creating nginx SSL configuration..."
        mkdir -p ./nginx-conf.d
        cat > ./nginx-conf.d/ssl.conf << 'EOF'
# HTTPS server configuration - automatically included when SSL certificates exist
server {
    listen 443 ssl;
    server_name supremecycle.in www.supremecycle.in;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    location / {
        proxy_pass http://app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }

    location /static/ {
        alias /var/www/static/;
    }
}

# Redirect HTTP to HTTPS for production
server {
    listen 80;
    server_name supremecycle.in www.supremecycle.in;
    return 301 https://$host$request_uri;
}
EOF

        # Comment out the HTTP server in main nginx.conf to avoid conflicts
        echo "📝 Updating main nginx.conf to disable HTTP when SSL is enabled..."
        cp nginx.conf nginx.conf.backup
        sed -i.bak '/# HTTP server/,/^    }$/s/^/#/' nginx.conf
        
        # Add a note in nginx.conf
        cat >> nginx.conf << 'EOF'
    
    # HTTP server disabled - SSL redirect enabled in conf.d/ssl.conf
EOF
        
        # Setup auto-renewal
        echo "🔄 Setting up auto-renewal..."
        (crontab -l 2>/dev/null; echo "0 3 * * * cd $(pwd) && sudo certbot renew --quiet && sudo cp /etc/letsencrypt/live/supremecycle.in/*.pem ./ssl/ && docker compose restart nginx") | crontab -
        
        # Start services with SSL
        echo "🚀 Starting services with HTTPS..."
        docker compose up -d
        
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

else
    echo "❌ Invalid option. Please choose 1 or 2."
    exit 1
fi
