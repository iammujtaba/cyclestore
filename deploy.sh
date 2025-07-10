#!/bin/bash

set -e

# echo "🔧 Updating & Installing Docker + Docker Compose..."
# sudo apt update
# sudo apt install -y docker.io docker-compose-plugin
# sudo systemctl enable docker
# sudo systemctl start docker

echo "📁 Cloning your project (assumes you already uploaded it)..."
# Skip this if project is already present; otherwise git clone it here

echo "📦 Booting Nginx for Certbot setup..."
docker compose up -d nginx

echo "⏳ Waiting 5 seconds for Nginx to stabilize..."
sleep 5

echo "📜 Running Certbot to issue SSL certificates..."
docker compose run --rm certbot

echo "✅ Certbot done. Enabling HTTPS in nginx.conf..."
# Enable HTTPS block in nginx.conf if not already done (optional step if scripted)

echo "🔁 Restarting Nginx with SSL..."
docker compose restart nginx

echo "🚀 Starting full app (FastAPI + Nginx) in background..."
docker compose up -d

echo "🎉 Done! Visit: https://supremecycle.in"
