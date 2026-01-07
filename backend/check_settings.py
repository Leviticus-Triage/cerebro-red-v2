#!/usr/bin/env python3
"""
Quick script to verify Settings are loaded correctly.
Run this to check if API_KEY_ENABLED is being read from .env
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import get_settings

# Clear cache to force fresh load
get_settings.cache_clear()

# Get fresh settings
settings = get_settings()

print("=" * 60)
print("CEREBRO-RED v2 - Settings Verification")
print("=" * 60)
print(f"\n✅ API_KEY_ENABLED: {settings.security.api_key_enabled}")
print(f"✅ API_KEY: {settings.security.api_key[:20]}..." if settings.security.api_key else "✅ API_KEY: None")
print(f"✅ CORS_ORIGINS: {settings.security.cors_origins}")
print(f"✅ DATABASE_URL: {settings.database.url}")
print(f"✅ OLLAMA_BASE_URL: {settings.ollama.base_url}")
print("\n" + "=" * 60)

if not settings.security.api_key_enabled:
    print("✅ API Key Authentication ist DEAKTIVIERT")
    print("✅ Backend sollte Requests ohne API-Key akzeptieren")
    print("\n⚠️  WICHTIG: Backend muss NEU GESTARTET werden!")
    print("   Im Backend-Terminal: Strg+C, dann:")
    print("   uvicorn main:app --host 0.0.0.0 --port 8889 --reload")
else:
    print("❌ API Key Authentication ist noch AKTIV!")
    print("❌ Prüfen Sie die .env Datei:")
    print(f"   backend/.env sollte enthalten: API_KEY_ENABLED=false")

print("=" * 60)

