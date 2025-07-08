#!/bin/bash
echo "🔍 Docker Troubleshooting Script"
echo "================================="

echo "📊 Checking running containers:"
docker ps

echo ""
echo "📋 Checking container logs:"
docker compose logs cyclestore --tail=20

echo ""
echo "🌐 Checking if application is accessible inside container:"
docker compose exec cyclestore curl -f http://localhost:8000/health || echo "❌ Health check failed"

echo ""
echo "🔗 Checking port mapping:"
docker port $(docker compose ps -q cyclestore)

echo ""
echo "🔍 Checking if application binds to 0.0.0.0:"
docker compose exec cyclestore netstat -tlnp | grep :8000 || echo "❌ Port 8000 not bound"

echo ""
echo "🌍 Testing external connectivity (if available):"
curl -f http://localhost:8000/health 2>/dev/null && echo "✅ Accessible from host" || echo "❌ Not accessible from host"

echo ""
echo "📡 EC2 Security Group Requirements:"
echo "   - Inbound rule: HTTP (80) from 0.0.0.0/0"
echo "   - Inbound rule: Custom TCP (8000) from 0.0.0.0/0"
echo "   - Inbound rule: HTTPS (443) from 0.0.0.0/0 (if using SSL)"
