# SSL Setup Instructions for supremecycle.in

## Prerequisites

1. **Domain DNS**: Ensure supremecycle.in points to your EC2 IP (13.201.4.201)
2. **AWS Security Group**: Open these ports:
   - Port 80 (HTTP) - for certificate generation and redirects
   - Port 443 (HTTPS) - for SSL traffic

### Update AWS Security Group
```bash
# In AWS Console > EC2 > Security Groups > Your SG > Inbound Rules
# Add these rules:

Type: HTTP
Port: 80
Source: 0.0.0.0/0

Type: HTTPS  
Port: 443
Source: 0.0.0.0/0
```

## Setup Steps

1. **Run the SSL setup script on your EC2 instance:**
   ```bash
   chmod +x setup_ssl.sh
   ./setup_ssl.sh
   ```

2. **The script will:**
   - Install Certbot
   - Generate SSL certificates for supremecycle.in and www.supremecycle.in
   - Copy certificates to the ./ssl/ directory
   - Set up auto-renewal
   - Start your application with HTTPS enabled

3. **Test the setup:**
   ```bash
   chmod +x test_ssl.sh
   ./test_ssl.sh
   ```

## What's Configured

- **HTTPS Server**: Runs on port 443 with SSL
- **HTTP Redirect**: All HTTP traffic redirects to HTTPS
- **Security Headers**: Enhanced security headers for HTTPS
- **Auto-Renewal**: Certificates renew automatically every 3 months
- **SSL Grade A**: Modern SSL configuration for best security

## Troubleshooting

If SSL setup fails:

1. **Check DNS propagation:**
   ```bash
   dig A supremecycle.in
   # Should return: 13.201.4.201
   ```

2. **Verify ports are open:**
   ```bash
   curl -I http://supremecycle.in
   # Should connect or redirect
   ```

3. **Check current services:**
   ```bash
   sudo netstat -tlnp | grep -E ':(80|443)'
   # Should show nginx or be empty
   ```

4. **Manual certificate generation:**
   ```bash
   sudo certbot certonly --standalone -d supremecycle.in -d www.supremecycle.in
   ```

## After SSL Setup

Your website will be available at:
- https://supremecycle.in (primary)
- https://www.supremecycle.in
- http://supremecycle.in (redirects to HTTPS)
- http://www.supremecycle.in (redirects to HTTPS)

Test SSL grade: https://www.ssllabs.com/ssltest/analyze.html?d=supremecycle.in
