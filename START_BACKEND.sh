#!/bin/bash
# Backend Start-Script für CEREBRO-RED v2
# Startet Backend entweder via Docker oder lokal

set -e

echo "🚀 CEREBRO-RED v2 - Backend Start"
echo "=================================="
echo ""

# Prüfe ob Backend bereits läuft
HEALTH_CHECK=$(curl -s -w "\n%{http_code}" http://localhost:9000/health 2>&1)
HTTP_CODE=$(echo "$HEALTH_CHECK" | tail -n1)
BODY=$(echo "$HEALTH_CHECK" | head -n-1)

if [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Backend läuft bereits auf http://localhost:9000"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
    exit 0
elif [ "$HTTP_CODE" != "" ]; then
    echo "⚠️  Port 8000 antwortet, aber Health-Check fehlgeschlagen (HTTP $HTTP_CODE)"
    echo "   Möglicherweise läuft ein anderer Service auf Port 8000"
    echo ""
fi

echo "⚠️  Backend läuft nicht. Starte Backend..."
echo ""

# Prüfe Docker
if command -v docker &> /dev/null && docker ps > /dev/null 2>&1; then
    echo "🐳 Docker verfügbar - Starte via Docker Compose..."
    docker compose up -d cerebro-backend
    
    echo ""
    echo "⏳ Warte auf Backend (max. 30 Sekunden)..."
    for i in {1..30}; do
        if curl -s http://localhost:9000/health > /dev/null 2>&1; then
            echo "✅ Backend läuft!"
            curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health
            exit 0
        fi
        sleep 1
        echo -n "."
    done
    echo ""
    echo "❌ Backend startet zu langsam. Prüfe Logs: docker compose logs cerebro-backend"
    exit 1
else
    echo "💻 Docker nicht verfügbar - Starte lokal..."
    echo ""
    echo "📋 Führen Sie manuell aus:"
    echo ""
    echo "   cd backend"
    echo "   source ../venv/bin/activate  # oder Ihr venv"
    echo "   uvicorn main:app --reload --port 8000"
    echo ""
    echo "   Oder in einem neuen Terminal:"
    echo "   cd cerebro-red-v2/backend"
    echo "   python3 -m uvicorn main:app --reload --port 8000"
    echo ""
    exit 1
fi
