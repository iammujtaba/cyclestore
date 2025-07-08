#!/bin/bash

echo "Testing SSL Configuration for supremecycle.in"
echo "=============================================="

# Test DNS resolution
echo "1. Testing DNS resolution..."
echo "supremecycle.in -> $(dig +short A supremecycle.in)"
echo "www.supremecycle.in -> $(dig +short A www.supremecycle.in)"
echo ""

# Test HTTP to HTTPS redirect
echo "2. Testing HTTP to HTTPS redirect..."
HTTP_RESPONSE=$(curl -s -I http://supremecycle.in | head -1)
echo "HTTP response: $HTTP_RESPONSE"

REDIRECT_LOCATION=$(curl -s -I http://supremecycle.in | grep -i location)
echo "Redirect: $REDIRECT_LOCATION"
echo ""

# Test HTTPS connectivity
echo "3. Testing HTTPS connectivity..."
HTTPS_RESPONSE=$(curl -s -I https://supremecycle.in | head -1)
echo "HTTPS response: $HTTPS_RESPONSE"
echo ""

# Test SSL certificate
echo "4. Testing SSL certificate..."
SSL_INFO=$(openssl s_client -connect supremecycle.in:443 -servername supremecycle.in </dev/null 2>/dev/null | openssl x509 -noout -subject -dates 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "SSL Certificate info:"
    echo "$SSL_INFO"
else
    echo "❌ SSL certificate test failed"
fi
echo ""

# Test security headers
echo "5. Testing security headers..."
SECURITY_HEADERS=$(curl -s -I https://supremecycle.in | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options)")
echo "Security headers:"
echo "$SECURITY_HEADERS"
echo ""

# Overall status
echo "6. Overall status..."
if curl -s https://supremecycle.in > /dev/null 2>&1; then
    echo "✅ HTTPS is working correctly!"
    echo ""
    echo "Your website is now secure and accessible at:"
    echo "- https://supremecycle.in"
    echo "- https://www.supremecycle.in"
    echo ""
    echo "Recommended next steps:"
    echo "1. Test SSL grade: https://www.ssllabs.com/ssltest/analyze.html?d=supremecycle.in"
    echo "2. Verify auto-renewal: sudo certbot renew --dry-run"
    echo "3. Update any hardcoded HTTP links to HTTPS"
else
    echo "❌ HTTPS is not working properly"
    echo ""
    echo "Check the following:"
    echo "1. Nginx is running: docker-compose ps"
    echo "2. SSL certificates exist: ls -la ./ssl/"
    echo "3. Port 443 is open in AWS security group"
    echo "4. Check nginx logs: docker-compose logs nginx"
fi
