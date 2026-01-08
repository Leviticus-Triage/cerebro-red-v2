# 🔐 API-Key Problem - 401 Unauthorized

## Problem identifiziert

**Fehler:** `GET http://localhost:8889/api/experiments 401 (Unauthorized)`

Das Backend erfordert einen API-Key für alle Requests, aber das Frontend sendet keinen!

---

## Lösung: API-Key-Authentifizierung deaktivieren (Development)

### Option 1: API-Key-Authentifizierung deaktivieren (EMPFOHLEN für Development)

In der `.env` Datei:

```bash
# API-Key-Authentifizierung deaktivieren für Development
API_KEY_ENABLED=false
```

**Schritte:**
1. Öffnen Sie: `/mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/.env`
2. Suchen Sie die Zeile: `API_KEY_ENABLED=true`
3. Ändern Sie zu: `API_KEY_ENABLED=false`
4. Speichern Sie die Datei
5. **Backend neu starten** (Strg+C, dann `uvicorn main:app --host 0.0.0.0 --port 8889 --reload`)

---

### Option 2: API-Key im Frontend konfigurieren (Production-Ready)

Falls Sie die API-Key-Authentifizierung behalten möchten:

1. **API-Key aus `.env` kopieren:**
   ```bash
   grep "API_KEY=" /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/.env
   ```

2. **Im Browser:**
   - Öffnen Sie die Browser-Konsole (F12)
   - Gehen Sie zum Tab "Application" → "Local Storage"
   - Fügen Sie einen neuen Key hinzu:
     - Key: `api_key`
     - Value: `<Ihr-API-Key-aus-.env>`

3. **Oder im Frontend-Code:**
   Das Frontend hat bereits einen Auth-Store (`authStore`), der den API-Key speichern kann.

---

## Empfohlene Lösung für Development

**Deaktivieren Sie die API-Key-Authentifizierung:**

```bash
# In .env:
API_KEY_ENABLED=false
```

Dann Backend neu starten:
```bash
cd /mnt/nvme0n1p5/danii/hexstrike-ai-kit/cerebro-red-v2/backend
uvicorn main:app --host 0.0.0.0 --port 8889 --reload
```

---

## Erwartetes Ergebnis

Nach dem Deaktivieren der API-Key-Authentifizierung:

✅ **Keine 401 Unauthorized Fehler mehr**  
✅ **API-Calls erfolgreich** (200 OK)  
✅ **Dashboard zeigt Daten** oder "No experiments yet"  
✅ **Alle Funktionen arbeiten**

---

**Status:** ⚠️ **AKTION ERFORDERLICH**  
**Nächster Schritt:** `.env` bearbeiten und Backend neu starten

