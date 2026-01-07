#!/usr/bin/env python3
"""
Professionelle Log-Analyse für CEREBRO-RED v2

Analysiert Audit-Logs und generiert detaillierte Statistiken für Experimente.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Any


def load_audit_logs(log_dir: Path) -> List[Dict[str, Any]]:
    """Lade alle Audit-Log-Einträge."""
    entries = []
    
    if not log_dir.exists():
        print(f"❌ Log-Verzeichnis nicht gefunden: {log_dir}")
        return entries
    
    for log_file in sorted(log_dir.glob("audit_*.jsonl")):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                        entries.append(entry)
                    except json.JSONDecodeError as e:
                        print(f"⚠️  JSON-Fehler in {log_file}:{line_num}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Fehler beim Lesen von {log_file}: {e}", file=sys.stderr)
    
    return entries


def analyze_experiments(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analysiere Experiment-Statistiken."""
    stats = {
        'total_experiments': set(),
        'total_entries': len(entries),
        'event_types': defaultdict(int),
        'strategies': defaultdict(int),
        'success_scores': defaultdict(list),
        'latencies': defaultdict(list),
        'tokens_used': defaultdict(list),
        'errors': [],
        'models': {
            'target': defaultdict(int),
            'attacker': defaultdict(int),
            'judge': defaultdict(int)
        }
    }
    
    for entry in entries:
        # Experiment-ID sammeln
        exp_id = entry.get('experiment_id')
        if exp_id:
            stats['total_experiments'].add(exp_id)
        
        # Event-Typen zählen
        event_type = entry.get('event_type', 'unknown')
        stats['event_types'][event_type] += 1
        
        # Strategien zählen
        strategy = entry.get('strategy')
        if strategy:
            stats['strategies'][strategy] += 1
        
        # Success Scores sammeln
        success_score = entry.get('success_score')
        if success_score is not None:
            strategy_key = strategy or 'unknown'
            stats['success_scores'][strategy_key].append(success_score)
        
        # Latenzen sammeln
        latency = entry.get('latency_ms')
        if latency:
            model = entry.get('model_target', 'unknown')
            stats['latencies'][model].append(latency)
        
        # Tokens sammeln
        tokens = entry.get('tokens_used')
        if tokens:
            model = entry.get('model_target', 'unknown')
            stats['tokens_used'][model].append(tokens)
        
        # Fehler sammeln
        if event_type == 'error' or entry.get('error'):
            stats['errors'].append({
                'timestamp': entry.get('timestamp'),
                'experiment_id': exp_id,
                'error': entry.get('error', 'Unknown error'),
                'metadata': entry.get('metadata', {})
            })
        
        # Model-Statistiken
        if entry.get('model_target'):
            stats['models']['target'][entry['model_target']] += 1
        if entry.get('model_attacker'):
            stats['models']['attacker'][entry['model_attacker']] += 1
        if entry.get('model_judge'):
            stats['models']['judge'][entry['model_judge']] += 1
    
    return stats


def print_statistics(stats: Dict[str, Any]):
    """Drucke formatierte Statistiken."""
    print("=" * 70)
    print("📊 CEREBRO-RED v2 - Log-Analyse Report")
    print("=" * 70)
    print()
    
    # Übersicht
    print(f"📈 Übersicht:")
    print(f"  • Experimente: {len(stats['total_experiments'])}")
    print(f"  • Log-Einträge: {stats['total_entries']}")
    print(f"  • Event-Typen: {len(stats['event_types'])}")
    print()
    
    # Event-Typen
    if stats['event_types']:
        print(f"📋 Event-Typen:")
        for event_type, count in sorted(stats['event_types'].items(), key=lambda x: -x[1]):
            print(f"  • {event_type:30s} {count:6d}")
        print()
    
    # Strategien
    if stats['strategies']:
        print(f"🎯 Strategie-Verteilung:")
        for strategy, count in sorted(stats['strategies'].items(), key=lambda x: -x[1]):
            scores = stats['success_scores'].get(strategy, [])
            if scores:
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                print(f"  • {strategy:30s} {count:4d} Versuche | "
                      f"Ø Score: {avg_score:5.2f} | "
                      f"Min: {min_score:4.1f} | Max: {max_score:4.1f}")
            else:
                print(f"  • {strategy:30s} {count:4d} Versuche | Keine Scores")
        print()
    
    # Latenz-Statistiken
    if stats['latencies']:
        print(f"⏱️  Latenz-Statistiken (ms):")
        for model, latencies in sorted(stats['latencies'].items()):
            avg_latency = sum(latencies) / len(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p95 = sorted(latencies)[int(len(latencies) * 0.95)] if len(latencies) > 20 else max_latency
            print(f"  • {model:30s} Ø: {avg_latency:7.0f} | "
                  f"Min: {min_latency:6.0f} | Max: {max_latency:6.0f} | "
                  f"P95: {p95:6.0f} (n={len(latencies)})")
        print()
    
    # Token-Statistiken
    if stats['tokens_used']:
        print(f"🔢 Token-Verbrauch:")
        for model, tokens_list in sorted(stats['tokens_used'].items()):
            total_tokens = sum(tokens_list)
            avg_tokens = total_tokens / len(tokens_list)
            print(f"  • {model:30s} Total: {total_tokens:8d} | "
                  f"Ø: {avg_tokens:7.0f} (n={len(tokens_list)})")
        print()
    
    # Model-Verteilung
    if any(stats['models'].values()):
        print(f"🤖 Model-Verteilung:")
        for role in ['target', 'attacker', 'judge']:
            if stats['models'][role]:
                print(f"  {role.capitalize()} Models:")
                for model, count in sorted(stats['models'][role].items(), key=lambda x: -x[1]):
                    print(f"    • {model:28s} {count:4d}")
        print()
    
    # Fehler
    if stats['errors']:
        print(f"⚠️  Fehler gefunden: {len(stats['errors'])}")
        print(f"  Letzte 5 Fehler:")
        for error in stats['errors'][-5:]:
            timestamp = error.get('timestamp', 'Unknown')
            error_msg = error.get('error', 'Unknown error')
            exp_id = error.get('experiment_id', 'Unknown')
            print(f"    • [{timestamp}] {error_msg[:60]}")
            print(f"      Experiment: {exp_id}")
        print()
    else:
        print(f"✅ Keine Fehler gefunden")
        print()


def main():
    """Hauptfunktion."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Analysiere CEREBRO-RED v2 Audit-Logs'
    )
    parser.add_argument(
        '--log-dir',
        type=Path,
        default=Path('./data/audit_logs'),
        help='Pfad zum Audit-Log-Verzeichnis (Standard: ./data/audit_logs)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Ausgabe-Datei für Report (optional)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Ausgabe als JSON'
    )
    
    args = parser.parse_args()
    
    # Logs laden
    print(f"📂 Lade Logs aus: {args.log_dir}")
    entries = load_audit_logs(args.log_dir)
    
    if not entries:
        print("❌ Keine Log-Einträge gefunden!")
        sys.exit(1)
    
    # Analysieren
    stats = analyze_experiments(entries)
    
    # Ausgabe
    if args.json:
        output = {
            'summary': {
                'total_experiments': len(stats['total_experiments']),
                'total_entries': stats['total_entries'],
                'event_types': dict(stats['event_types']),
            },
            'strategies': {
                k: {
                    'count': stats['strategies'][k],
                    'avg_score': sum(v) / len(v) if v else 0,
                    'scores': v
                }
                for k, v in stats['success_scores'].items()
            },
            'latencies': {
                k: {
                    'avg': sum(v) / len(v),
                    'min': min(v),
                    'max': max(v),
                    'count': len(v)
                }
                for k, v in stats['latencies'].items()
            },
            'errors': stats['errors']
        }
        
        output_str = json.dumps(output, indent=2, default=str)
        
        if args.output:
            args.output.write_text(output_str)
            print(f"✅ JSON-Report gespeichert: {args.output}")
        else:
            print(output_str)
    else:
        # Text-Report
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                import io
                from contextlib import redirect_stdout
                
                output_buffer = io.StringIO()
                with redirect_stdout(output_buffer):
                    print_statistics(stats)
                
                f.write(output_buffer.getvalue())
                print(f"✅ Report gespeichert: {args.output}")
        else:
            print_statistics(stats)


if __name__ == "__main__":
    main()
