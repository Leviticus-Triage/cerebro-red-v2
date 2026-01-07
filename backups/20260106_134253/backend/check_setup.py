#!/usr/bin/env python3
"""
Setup-Verifikationsskript für CEREBRO-RED v2 Tests.

Führt alle notwendigen Checks durch, bevor Tests ausgeführt werden.
"""

import sys
import os
from pathlib import Path

def check_directory():
    """Prüft ob wir im richtigen Verzeichnis sind."""
    current_dir = Path.cwd()
    expected_dir = Path("/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend")
    
    if current_dir != expected_dir:
        print(f"❌ Falsches Verzeichnis!")
        print(f"   Aktuell: {current_dir}")
        print(f"   Erwartet: {expected_dir}")
        print(f"\n   Lösung: cd {expected_dir}")
        return False
    
    print(f"✅ Verzeichnis OK: {current_dir}")
    return True

def check_dependencies():
    """Prüft ob alle Dependencies installiert sind."""
    required_modules = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "litellm",
        "pytest",
        "pytest_asyncio"
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} installiert")
        except ImportError:
            print(f"❌ {module} NICHT installiert")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Fehlende Dependencies: {', '.join(missing)}")
        print(f"   Lösung: pip3 install -r requirements.txt")
        return False
    
    return True

def check_env_file():
    """Prüft ob .env Datei existiert und konfiguriert ist."""
    env_path = Path("../.env")
    
    if not env_path.exists():
        print(f"❌ .env Datei nicht gefunden: {env_path}")
        print(f"   Lösung: cp ../.env.example ../.env")
        return False
    
    print(f"✅ .env Datei existiert: {env_path}")
    
    # Prüfe wichtige Einstellungen
    with open(env_path) as f:
        content = f.read()
        if "DEFAULT_LLM_PROVIDER" not in content:
            print(f"⚠️  .env scheint nicht konfiguriert zu sein")
            print(f"   Lösung: nano ../.env")
            return False
    
    print(f"✅ .env scheint konfiguriert zu sein")
    return True

def check_directories():
    """Prüft ob notwendige Verzeichnisse existieren."""
    required_dirs = [
        "../data/experiments",
        "../data/audit_logs",
        "../data/results"
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"✅ Verzeichnis existiert: {dir_path}")
        else:
            print(f"❌ Verzeichnis fehlt: {dir_path}")
            print(f"   Lösung: mkdir -p {dir_path}")
            all_ok = False
    
    return all_ok

def check_ollama():
    """Prüft Ollama Connectivity."""
    import subprocess
    
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ Ollama läuft")
            if "qwen3:8b" in result.stdout:
                print(f"✅ qwen3:8b verfügbar")
            else:
                print(f"⚠️  qwen3:8b nicht gefunden")
                print(f"   Lösung: ollama pull qwen3:8b")
            
            if "qwen3:14b" in result.stdout:
                print(f"✅ qwen3:14b verfügbar")
            else:
                print(f"⚠️  qwen3:14b nicht gefunden")
                print(f"   Lösung: ollama pull qwen3:14b")
            
            return True
        else:
            print(f"❌ Ollama nicht erreichbar")
            print(f"   Lösung: ollama serve (in neuem Terminal)")
            return False
    except FileNotFoundError:
        print(f"❌ Ollama nicht installiert")
        print(f"   Lösung: https://ollama.ai/download")
        return False
    except subprocess.TimeoutExpired:
        print(f"❌ Ollama Timeout")
        print(f"   Lösung: ollama serve (in neuem Terminal)")
        return False

def check_database():
    """Prüft ob Database initialisiert ist."""
    db_path = Path("../data/experiments/cerebro.db")
    
    if db_path.exists():
        print(f"✅ Database existiert: {db_path}")
        return True
    else:
        print(f"⚠️  Database nicht initialisiert: {db_path}")
        print(f"   Lösung: alembic upgrade head")
        return False

def check_imports():
    """Prüft ob Module importierbar sind."""
    sys.path.insert(0, '.')
    
    try:
        from core.models import ExperimentConfig
        print(f"✅ core.models importierbar")
    except ImportError as e:
        print(f"❌ core.models nicht importierbar: {e}")
        return False
    
    try:
        from utils.config import get_settings
        print(f"✅ utils.config importierbar")
    except ImportError as e:
        print(f"❌ utils.config nicht importierbar: {e}")
        return False
    
    return True

def main():
    """Hauptfunktion - führt alle Checks aus."""
    print("=" * 60)
    print("CEREBRO-RED v2 - Setup-Verifikation")
    print("=" * 60)
    print()
    
    checks = [
        ("Verzeichnis", check_directory),
        ("Dependencies", check_dependencies),
        ("Environment", check_env_file),
        ("Verzeichnisse", check_directories),
        ("Ollama", check_ollama),
        ("Database", check_database),
        ("Imports", check_imports),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n📋 Prüfe {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Fehler bei {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 60)
    print("Zusammenfassung:")
    print("=" * 60)
    
    all_ok = True
    for name, result in results:
        status = "✅ OK" if result else "❌ FEHLER"
        print(f"{status:10} {name}")
        if not result:
            all_ok = False
    
    print()
    if all_ok:
        print("🎉 Alle Checks bestanden! Sie können jetzt Tests ausführen:")
        print("   pytest tests/test_ollama_connectivity.py -v -s")
    else:
        print("⚠️  Einige Checks fehlgeschlagen. Bitte beheben Sie die Fehler oben.")
        print("   Siehe: START_HIER.md für detaillierte Anleitung")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

