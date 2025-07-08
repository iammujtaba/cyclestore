#!/bin/bash
echo "🚀 Quick Fix for Docker Deployment on EC2"
echo "=========================================="

echo "1. 🛑 Stopping existing containers..."
docker compose down

echo "2. 🔧 Rebuilding with latest changes..."
docker compose build --no-cache

echo "3. 🚀 Starting containers..."
docker compose up -d

echo "4. ⏳ Waiting for containers to start..."
sleep 10

echo "5. 📊 Checking container status..."
docker compose ps

echo "6. 📋 Checking logs..."
docker compose logs cyclestore --tail=10

echo "7. 🌐 Testing health endpoint..."
sleep 5
docker compose exec cyclestore curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Health check passed" || echo "❌ Health check failed"

echo ""
echo "🔗 Your application should now be accessible at:"
echo "   http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4 2>/dev/null || echo 'YOUR-EC2-IP')/"
echo "   http://supremecycle.in/ (if DNS is configured)"
echo ""
echo "📡 Make sure your EC2 Security Group allows:"
echo "   - Inbound TCP port 80 from 0.0.0.0/0 (HTTP)"
echo "   - Inbound TCP port 443 from 0.0.0.0/0 (HTTPS - for future SSL)"
echo "   - NO need to expose port 8000 (nginx handles routing)"

echo ""
echo "🔍 If still not working, run: ./troubleshoot_docker.sh"
