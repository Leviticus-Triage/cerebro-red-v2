#!/bin/bash
# Quick Test Examples für CEREBRO-RED v2
# Vollständige, funktionierende curl-Beispiele

set -e

API_URL="http://localhost:9000"
API_KEY="test-api-key"

echo "🧪 CEREBRO-RED v2 - Quick Test Examples"
echo "========================================"
echo ""

# Prüfe ob Backend läuft
echo "🔍 Prüfe Backend-Status..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL/health" 2>&1)
HTTP_CODE=$(echo "$HEALTH_RESPONSE" | tail -n1)
BODY=$(echo "$HEALTH_RESPONSE" | head -n-1)

if [ "$HTTP_CODE" != "200" ]; then
    echo "❌ Backend läuft NICHT! (HTTP $HTTP_CODE)"
    echo "   Response: $BODY"
    echo ""
    echo "📋 Backend starten:"
    echo "   Option 1 (Script):  ./START_BACKEND.sh"
    echo "   Option 2 (Docker):   docker compose up -d cerebro-backend"
    echo "   Option 3 (Lokal):    cd backend && uvicorn main:app --reload --port 8000"
    echo ""
    echo "   WICHTIG: Backend muss auf http://localhost:8000 laufen!"
    echo "   Prüfe nach Start: curl http://localhost:8000/health"
    echo ""
    echo "   Siehe auch: TROUBLESHOOTING_BACKEND.md"
    echo ""
    echo "   Dann erneut ausführen: ./QUICK_TEST_EXAMPLES.sh"
    exit 1
fi

echo "✅ Backend läuft!"
echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
echo ""
echo ""

# Test 1: Health Check (wiederholen für saubere Ausgabe)
echo "1️⃣ Health Check"
curl -s "$API_URL/health" | jq . || echo "Fehler beim Health Check"
echo ""
echo ""

# Test 2: Experiment erstellen (Ollama)
echo "2️⃣ Experiment erstellen (Ollama)"
EXPERIMENT_ID=$(uuidgen 2>/dev/null || python3 -c "import uuid; print(uuid.uuid4())")
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/experiments" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"experiment_id\": \"$EXPERIMENT_ID\",
    \"name\": \"Quick Test - Ollama\",
    \"description\": \"Schneller Test mit Ollama\",
    \"target_model_provider\": \"ollama\",
    \"target_model_name\": \"qwen2.5:3b\",
    \"attacker_model_provider\": \"ollama\",
    \"attacker_model_name\": \"qwen3:8b\",
    \"judge_model_provider\": \"ollama\",
    \"judge_model_name\": \"qwen3:8b\",
    \"initial_prompts\": [\"Test prompt\"],
    \"strategies\": [\"roleplay_injection\"],
    \"max_iterations\": 3,
    \"max_concurrent_attacks\": 1,
    \"success_threshold\": 7.0,
    \"timeout_seconds\": 300
  }")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo "✅ Experiment erstellt (HTTP $HTTP_CODE)"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
else
    echo "❌ Fehler beim Erstellen (HTTP $HTTP_CODE)"
    echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
    echo ""
    echo "💡 Tipp: Prüfe ob alle required fields vorhanden sind"
fi
echo ""
echo ""

# Test 3: Scan starten
echo "3️⃣ Scan starten"
SCAN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/api/scan/start" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"experiment_config\": {
      \"experiment_id\": \"$EXPERIMENT_ID\",
      \"name\": \"Quick Test - Ollama\",
      \"description\": \"Schneller Test mit Ollama\",
    \"target_model_provider\": \"ollama\",
    \"target_model_name\": \"qwen2.5:3b\",
    \"attacker_model_provider\": \"ollama\",
    \"attacker_model_name\": \"qwen3:8b\",
    \"judge_model_provider\": \"ollama\",
    \"judge_model_name\": \"qwen3:8b\",
      \"initial_prompts\": [\"Test prompt\"],
      \"strategies\": [\"roleplay_injection\"],
      \"max_iterations\": 3,
      \"max_concurrent_attacks\": 1,
      \"success_threshold\": 7.0,
      \"timeout_seconds\": 300
    }
  }")

SCAN_HTTP_CODE=$(echo "$SCAN_RESPONSE" | tail -n1)
SCAN_BODY=$(echo "$SCAN_RESPONSE" | head -n-1)

if [ "$SCAN_HTTP_CODE" = "200" ] || [ "$SCAN_HTTP_CODE" = "202" ]; then
    echo "✅ Scan gestartet (HTTP $SCAN_HTTP_CODE)"
    echo "$SCAN_BODY" | jq . 2>/dev/null || echo "$SCAN_BODY"
else
    echo "❌ Fehler beim Starten (HTTP $SCAN_HTTP_CODE)"
    echo "$SCAN_BODY" | jq . 2>/dev/null || echo "$SCAN_BODY"
    echo ""
    echo "💡 Tipp: Prüfe ob Experiment existiert oder Ollama läuft"
fi
echo ""
echo ""

# Test 4: Scan Status prüfen
echo "4️⃣ Scan Status prüfen"
sleep 2
STATUS_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/api/scan/status/$EXPERIMENT_ID" \
  -H "X-API-Key: $API_KEY")

STATUS_HTTP_CODE=$(echo "$STATUS_RESPONSE" | tail -n1)
STATUS_BODY=$(echo "$STATUS_RESPONSE" | head -n-1)

if [ "$STATUS_HTTP_CODE" = "200" ]; then
    echo "✅ Status abgerufen (HTTP $STATUS_HTTP_CODE)"
    echo "$STATUS_BODY" | jq . 2>/dev/null || echo "$STATUS_BODY"
else
    echo "⚠️  Status nicht verfügbar (HTTP $STATUS_HTTP_CODE)"
    echo "$STATUS_BODY" | jq . 2>/dev/null || echo "$STATUS_BODY"
    echo ""
    echo "💡 Tipp: Scan wurde möglicherweise noch nicht gestartet"
fi
echo ""
echo ""

echo "✅ Quick Tests abgeschlossen!"
echo ""
echo "📊 Weitere Tests:"
echo "   - Siehe PROFESSIONAL_TESTING_GUIDE.md für umfassende Beispiele"
echo "   - Siehe README.md für Cloud OpenAI Tests"
