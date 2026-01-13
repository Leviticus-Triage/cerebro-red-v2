#!/bin/bash
#
# CEREBRO-RED v2 - Live Monitoring Script
# ========================================
#
# Usage:
#   ./LIVE_MONITOR.sh [mode]
#
# Modes:
#   all       - Alle Logs (Docker + Audit + Verbose)
#   docker    - Nur Docker Backend Logs
#   audit     - Nur Audit Logs (strukturierte Events)
#   verbose   - Nur Verbose Logs (LLM Details)
#   llm       - Nur LLM Request/Response Logs
#   errors    - Nur Fehler
#
# Keyboard:
#   Ctrl+C    - Beenden
#

set -e

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'
DIM='\033[2m'

# Logo
print_logo() {
    echo -e "${CYAN}${BOLD}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║    CEREBRO-RED v2 - Live Monitoring                     ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Mode selection
MODE=${1:-all}
print_logo

echo -e "${YELLOW} Mode: ${BOLD}$MODE${NC}"
echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2

case $MODE in
    "docker"|"d")
        echo -e "${GREEN} Docker Backend Logs (Live)${NC}"
        echo -e "${DIM}Zeigt alle Backend-Aktivitäten${NC}"
        echo ""
        docker compose logs -f cerebro-backend 2>&1 | while read line; do
            # Farbcodierung nach Inhalt
            if echo "$line" | grep -q "ERROR\|Exception\|Failed"; then
                echo -e "${RED}$line${NC}"
            elif echo "$line" | grep -q "WARNING"; then
                echo -e "${YELLOW}$line${NC}"
            elif echo "$line" | grep -q "LLM\|Request\|Response"; then
                echo -e "${MAGENTA}$line${NC}"
            elif echo "$line" | grep -q "Iteration\|Score"; then
                echo -e "${CYAN}$line${NC}"
            elif echo "$line" | grep -q "SUCCESS\|Jailbreak\|Vulnerability"; then
                echo -e "${GREEN}${BOLD}$line${NC}"
            else
                echo "$line"
            fi
        done
        ;;
    
    "audit"|"a")
        echo -e "${BLUE} Audit Logs (Live)${NC}"
        echo -e "${DIM}Strukturierte Events im JSONL-Format${NC}"
        echo ""
        
        # Finde das neueste Audit-Log im Container
        LATEST_LOG=$(docker compose exec cerebro-backend ls -t /app/data/audit_logs/ 2>/dev/null | head -1)
        
        if [ -z "$LATEST_LOG" ]; then
            echo -e "${YELLOW}️  Keine Audit-Logs gefunden. Starte ein Experiment zuerst.${NC}"
            exit 1
        fi
        
        echo -e "${DIM}Log file: $LATEST_LOG${NC}"
        echo ""
        
        docker compose exec cerebro-backend tail -f "/app/data/audit_logs/$LATEST_LOG" 2>&1 | while read line; do
            # Parse JSON und formatiere
            EVENT=$(echo "$line" | jq -r '.event_type // "unknown"' 2>/dev/null)
            ITER=$(echo "$line" | jq -r '.iteration_number // "N/A"' 2>/dev/null)
            STRATEGY=$(echo "$line" | jq -r '.strategy // .metadata.strategy // "N/A"' 2>/dev/null)
            SCORE=$(echo "$line" | jq -r '.metadata.score // .score // "N/A"' 2>/dev/null)
            
            case $EVENT in
                "experiment_start")
                    echo -e "${GREEN}${BOLD} EXPERIMENT STARTED${NC}"
                    echo "$line" | jq -r '"   ID: \(.experiment_id)\n   Name: \(.experiment_name // "N/A")"' 2>/dev/null
                    ;;
                "experiment_complete"|"experiment_completed")
                    echo -e "${GREEN}${BOLD} EXPERIMENT COMPLETED${NC}"
                    ;;
                "iteration_start")
                    echo -e "${CYAN} Iteration $ITER started${NC} ${DIM}(Strategy: $STRATEGY)${NC}"
                    ;;
                "iteration_complete"|"iteration_completed")
                    if [ "$SCORE" != "N/A" ] && [ "$SCORE" != "null" ]; then
                        if (( $(echo "$SCORE >= 7" | bc -l 2>/dev/null || echo 0) )); then
                            echo -e "${GREEN} Iteration $ITER: Score $SCORE${NC}"
                        else
                            echo -e "${YELLOW} Iteration $ITER: Score $SCORE${NC}"
                        fi
                    else
                        echo -e "${YELLOW} Iteration $ITER completed${NC}"
                    fi
                    ;;
                "mutation")
                    echo -e "${MAGENTA} Mutation applied${NC} ${DIM}($STRATEGY)${NC}"
                    ;;
                "judge_evaluation")
                    echo -e "${BLUE}️  Judge Score: $SCORE${NC}"
                    ;;
                "llm_request")
                    echo -e "${DIM}→ LLM Request${NC}"
                    ;;
                "llm_response")
                    echo -e "${DIM}← LLM Response${NC}"
                    ;;
                "vulnerability_found")
                    echo -e "${RED}${BOLD} VULNERABILITY FOUND!${NC}"
                    echo "$line" | jq '.' 2>/dev/null
                    ;;
                "error")
                    echo -e "${RED} ERROR: $(echo "$line" | jq -r '.error_type // .message // "Unknown"')${NC}"
                    ;;
                *)
                    echo -e "${DIM}• $EVENT${NC}"
                    ;;
            esac
        done
        ;;
    
    "verbose"|"v")
        echo -e "${MAGENTA} Verbose Logs (Live)${NC}"
        echo -e "${DIM}Detaillierte LLM und Code Flow Logs${NC}"
        echo ""
        
        # Finde das neueste Verbose-Log
        VERBOSE_LOG=$(docker compose exec cerebro-backend ls -t /tmp/cerebro_logs/ 2>/dev/null | head -1)
        
        if [ -z "$VERBOSE_LOG" ]; then
            echo -e "${YELLOW}️  Keine Verbose-Logs gefunden.${NC}"
            echo -e "${DIM}Starte ein Experiment mit CEREBRO_VERBOSITY=3${NC}"
            exit 1
        fi
        
        echo -e "${DIM}Log file: $VERBOSE_LOG${NC}"
        echo ""
        
        docker compose exec cerebro-backend tail -f "/tmp/cerebro_logs/$VERBOSE_LOG" 2>&1
        ;;
    
    "llm"|"l")
        echo -e "${CYAN} LLM Requests/Responses (Live)${NC}"
        echo -e "${DIM}Nur LLM-bezogene Events${NC}"
        echo ""
        
        docker compose logs -f cerebro-backend 2>&1 | grep --line-buffered -E "LLM|Request|Response|→|←|Token|latency" | while read line; do
            if echo "$line" | grep -q "Request\|→"; then
                echo -e "${CYAN}$line${NC}"
            elif echo "$line" | grep -q "Response\|←"; then
                echo -e "${MAGENTA}$line${NC}"
            else
                echo "$line"
            fi
        done
        ;;
    
    "errors"|"e")
        echo -e "${RED} Errors Only (Live)${NC}"
        echo ""
        
        docker compose logs -f cerebro-backend 2>&1 | grep --line-buffered -iE "error|exception|failed|traceback|critical" | while read line; do
            echo -e "${RED}$line${NC}"
        done
        ;;
    
    "all"|*)
        echo -e "${GREEN} All Logs (Combined View)${NC}"
        echo -e "${DIM}Docker Backend + Key Events${NC}"
        echo ""
        echo -e "${YELLOW}Tipp: Für spezifische Logs nutze:${NC}"
        echo -e "  ${DIM}./LIVE_MONITOR.sh docker   - Docker Logs${NC}"
        echo -e "  ${DIM}./LIVE_MONITOR.sh audit    - Audit Events${NC}"
        echo -e "  ${DIM}./LIVE_MONITOR.sh verbose  - Verbose Details${NC}"
        echo -e "  ${DIM}./LIVE_MONITOR.sh llm      - LLM Calls${NC}"
        echo -e "  ${DIM}./LIVE_MONITOR.sh errors   - Nur Fehler${NC}"
        echo ""
        echo -e "${DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo ""
        
        # Kombinierte Ansicht
        docker compose logs -f cerebro-backend 2>&1 | while read line; do
            # Farbcodierung
            if echo "$line" | grep -qE "ERROR|Exception|Failed|CRITICAL"; then
                echo -e "${RED}$line${NC}"
            elif echo "$line" | grep -q "WARNING"; then
                echo -e "${YELLOW}$line${NC}"
            elif echo "$line" | grep -qE "Iteration.*started|"; then
                echo -e "${CYAN}${BOLD}$line${NC}"
            elif echo "$line" | grep -qE "Score|️|Judge"; then
                echo -e "${BLUE}$line${NC}"
            elif echo "$line" | grep -qE "SUCCESS|Jailbreak|Vulnerability|"; then
                echo -e "${GREEN}${BOLD}$line${NC}"
            elif echo "$line" | grep -qE "LLM|→|←|Request|Response"; then
                echo -e "${MAGENTA}$line${NC}"
            elif echo "$line" | grep -qE "POST|GET|PUT|DELETE|WebSocket"; then
                echo -e "${DIM}$line${NC}"
            else
                echo "$line"
            fi
        done
        ;;
esac
