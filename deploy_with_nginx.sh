#!/bin/bash
echo "🌐 Nginx + FastAPI Deployment Script"
echo "===================================="

echo "1. 🛑 Stopping all containers..."
docker compose down

echo "2. 🔧 Rebuilding application..."
docker compose build --no-cache cyclestore

echo "3. 🚀 Starting with Nginx reverse proxy..."
docker compose up -d

echo "4. ⏳ Waiting for services to start..."
sleep 15

echo "5. 📊 Checking container status..."
docker compose ps

echo "6. 📋 Checking application logs..."
echo "--- FastAPI App Logs ---"
docker compose logs cyclestore --tail=5

echo ""
echo "--- Nginx Logs ---"
docker compose logs nginx --tail=5

echo ""
echo "7. 🧪 Testing health endpoints..."

echo "   Testing FastAPI directly..."
docker compose exec cyclestore curl -f http://localhost:8000/health 2>/dev/null && echo "✅ FastAPI OK" || echo "❌ FastAPI Failed"

echo "   Testing through Nginx..."
sleep 2
curl -f http://localhost/health 2>/dev/null && echo "✅ Nginx routing OK" || echo "❌ Nginx routing failed"

echo ""
echo "8. 📡 Network configuration check..."
docker compose exec nginx cat /etc/nginx/nginx.conf | grep -A 5 "upstream cyclestore_app" || echo "❌ Nginx config issue"

echo ""
echo "🎉 Deployment Summary:"
echo "========================"
echo "✅ Application: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo '13.201.4.201')/"
echo "✅ Admin Panel: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo '13.201.4.201')/admin"
echo "✅ Domain: http://supremecycle.in/ (when DNS is configured)"

echo ""
echo "🔒 Security Group Requirements:"
echo "   - HTTP (port 80): ✅ Required"
echo "   - HTTPS (port 443): 🔄 For future SSL"
echo "   - Port 8000: ❌ NOT needed (internal only)"

echo ""
echo "🔍 If still having issues:"
echo "   1. Check EC2 Security Group for port 80"
echo "   2. Run: docker compose logs nginx"
echo "   3. Run: ./troubleshoot_docker.sh"
