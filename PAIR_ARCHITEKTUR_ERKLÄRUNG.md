# 🎯 PAIR Algorithm - Architektur-Erklärung

## Warum drei verschiedene LLMs?

Der **PAIR Algorithm** (Prompt Automatic Iterative Refinement) verwendet eine **drei-LLM-Architektur**, weil jedes LLM eine spezifische Rolle hat:

### 1. **Attacker LLM (A)** - Angreifer
**Rolle:** Generiert und verfeinert Angriffs-Prompts

**Warum stärker sein sollte:**
- Muss intelligente, adaptive Angriffsstrategien entwickeln
- Benötigt besseres Verständnis für Prompt-Engineering
- Sollte aus vorherigen Fehlschlägen lernen können

**Beispiel:** `qwen3:8b` (größeres Modell)

### 2. **Target LLM (T)** - Ziel
**Rolle:** Das zu testende Modell, das angegriffen wird

**Warum schwächer sein kann:**
- Dies ist das Modell, dessen Sicherheit getestet wird
- Kann kleiner/schwächer sein - genau das wird getestet
- Sollte die "normale" Produktions-Version sein

**Beispiel:** `qwen2.5:3b` (kleineres Modell)

### 3. **Judge LLM (J)** - Bewerter
**Rolle:** Bewertet, ob ein Angriff erfolgreich war

**Warum stärker sein sollte:**
- Muss subtile Sicherheitsverletzungen erkennen
- Benötigt gutes Verständnis für Harmful Content
- Sollte Chain-of-Thought Reasoning durchführen können

**Beispiel:** `qwen3:8b` (größeres Modell)

---

## ❌ Falsche Konfiguration

```json
{
  "target_model_name": "qwen2.5:3b",
  "attacker_model_name": "qwen2.5:3b",  // ❌ Gleiches Modell!
  "judge_model_name": "qwen2.5:3b"      // ❌ Gleiches Modell!
}
```

**Problem:** Ein Modell kann sich nicht effektiv selbst pentesten!

---

## ✅ Korrekte Konfiguration

```json
{
  "target_model_name": "qwen2.5:3b",     // ✅ Zu testendes Modell (kann schwächer sein)
  "attacker_model_name": "qwen3:8b",     // ✅ Stärkeres Modell für bessere Angriffe
  "judge_model_name": "qwen3:8b"         // ✅ Stärkeres Modell für bessere Bewertung
}
```

**Vorteil:** 
- Stärkeres Modell generiert bessere Angriffs-Prompts
- Stärkeres Modell bewertet genauer
- Schwächeres Modell wird realistisch getestet

---

## 📊 PAIR Algorithm Flow

```
┌─────────────┐
│ Attacker    │  (qwen3:8b - stärker)
│ LLM (A)     │
└──────┬──────┘
       │ Generiert pᵢ (mutated prompt)
       ▼
┌─────────────┐
│ Target      │  (qwen2.5:3b - zu testen)
│ LLM (T)     │
└──────┬──────┘
       │ Antwortet rᵢ
       ▼
┌─────────────┐
│ Judge       │  (qwen3:8b - stärker)
│ LLM (J)     │
└──────┬──────┘
       │ Bewertet sᵢ (score)
       ▼
   Feedback → Attacker (für nächste Iteration)
```

---

## 🎯 Best Practices

### Für Production-Tests:
- **Target**: Produktions-Modell (z.B. `gpt-3.5-turbo`)
- **Attacker**: Stärkeres Modell (z.B. `gpt-4`)
- **Judge**: Stärkeres Modell (z.B. `gpt-4`)

### Für Local-Tests (Ollama):
- **Target**: `qwen2.5:3b` (kleiner, schneller)
- **Attacker**: `qwen3:8b` (größer, intelligenter)
- **Judge**: `qwen3:8b` (größer, genauer)

### Für Budget-Optimierung:
- **Target**: Kleines Modell
- **Attacker**: Großes Modell (wichtig für gute Angriffe)
- **Judge**: Großes Modell (wichtig für genaue Bewertung)

---

## 📚 Referenzen

- **PAIR Paper**: [Jailbreaking Black Box Large Language Models in Twenty Queries](https://arxiv.org/abs/2310.08419)
- Algorithm 1 beschreibt die drei-LLM-Architektur explizit

---

**Wichtig:** Attacker und Judge sollten **immer stärker oder gleich stark** wie das Target sein, um effektive Tests durchzuführen!
