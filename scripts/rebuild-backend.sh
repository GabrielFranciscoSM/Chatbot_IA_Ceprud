#!/bin/bash
# Quick script to rebuild and restart the backend container

cd /home/gabriel/clase/TFG/Practicas/Chatbot_IA_Ceprud

echo "Stopping all containers..."
podman-compose -f ../docker-compose-full.yml down

echo "Rebuilding backend..."
podman-compose -f ../docker-compose-full.yml build backend

echo "Starting all containers..."
podman-compose -f ../docker-compose-full.yml up -d

echo "Done! Checking backend status..."
