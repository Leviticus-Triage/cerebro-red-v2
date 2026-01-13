"""
backend/utils/live_logger.py
============================

Live Logging System für CEREBRO-RED v2

Verbosity Levels:
- 0: MINIMAL   - Nur Errors
- 1: NORMAL    - + Warnings, wichtige Events (Experiment Start/Ende)
- 2: VERBOSE   - + LLM Requests/Responses, Iterations, Scores
- 3: DEBUG     - + Full Code Flow, alle Details

Usage:
    from utils.live_logger import live_logger
    
    live_logger.llm_request("Generating attack prompt...")
    live_logger.llm_response("Response received", tokens=150)
    live_logger.code_flow("orchestrator.run_experiment", "Starting iteration 1")
"""

import sys
import logging
from datetime import datetime
from typing import Optional, Any, Dict
from functools import lru_cache
from enum import IntEnum
import json


class VerbosityLevel(IntEnum):
    """Verbosity levels for logging."""
    MINIMAL = 0   # Nur Errors
    NORMAL = 1    # + Warnings, wichtige Events
    VERBOSE = 2   # + LLM Requests/Responses
    DEBUG = 3     # + Full Code Flow


class LiveLogger:
    """
    Live Logger für Real-Time Monitoring von CEREBRO-RED v2.
    
    Unterstützt:
    - Farbige Console-Ausgabe
    - Verbosity Level Filtering
    - LLM Stream Logging
    - Code Flow Tracking
    - Structured JSON Logging
    """
    
    # ANSI Color Codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        "bg_red": "\033[41m",
        "bg_green": "\033[42m",
        "bg_blue": "\033[44m",
    }
    
    # Event Type Icons
    ICONS = {
        "llm_request": "",
        "llm_response": "",
        "llm_stream": "",
        "iteration": "",
        "attack": "️",
        "judge": "️",
        "mutation": "",
        "score": "",
        "success": "",
        "failure": "",
        "warning": "️",
        "error": "",
        "code_flow": "",
        "experiment": "",
        "database": "",
        "websocket": "",
    }
    
    def __init__(self):
        self._verbosity = VerbosityLevel.VERBOSE
        self._stream_llm = True
        self._stream_code_flow = True
        self._use_colors = True
        self._logger = logging.getLogger("cerebro.live")
        self._setup_handler()
    
    def _setup_handler(self):
        """Setup console handler with custom formatting."""
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.DEBUG)
    
    def configure(self, verbosity: int = 2, stream_llm: bool = True, 
                  stream_code_flow: bool = True, use_colors: bool = True):
        """Configure the live logger."""
        self._verbosity = VerbosityLevel(min(max(verbosity, 0), 3))
        self._stream_llm = stream_llm
        self._stream_code_flow = stream_code_flow
        self._use_colors = use_colors
    
    def _color(self, text: str, color: str) -> str:
        """Apply color to text if colors are enabled."""
        if not self._use_colors:
            return text
        return f"{self.COLORS.get(color, '')}{text}{self.COLORS['reset']}"
    
    def _timestamp(self) -> str:
        """Get formatted timestamp."""
        return datetime.now().strftime("%H:%M:%S.%f")[:-3]
    
    def _format_message(self, event_type: str, message: str, 
                        details: Optional[Dict[str, Any]] = None,
                        color: str = "white") -> str:
        """Format a log message with icon, timestamp, and details."""
        icon = self.ICONS.get(event_type, "•")
        ts = self._color(f"[{self._timestamp()}]", "dim")
        event = self._color(f"[{event_type.upper():12}]", color)
        msg = self._color(message, color)
        
        formatted = f"{ts} {icon} {event} {msg}"
        
        if details and self._verbosity >= VerbosityLevel.VERBOSE:
            detail_str = " | ".join(f"{k}={v}" for k, v in details.items())
            formatted += f" {self._color(f'({detail_str})', 'dim')}"
        
        return formatted
    
    def _log(self, level: VerbosityLevel, event_type: str, message: str,
             details: Optional[Dict[str, Any]] = None, color: str = "white"):
        """Internal log method with verbosity check."""
        if self._verbosity < level:
            return
        
        formatted = self._format_message(event_type, message, details, color)
        self._logger.info(formatted)
    
    # ============= PUBLIC API =============
    
    def experiment_start(self, experiment_id: str, name: str, 
                         target_model: str, strategies: list):
        """Log experiment start event."""
        self._log(
            VerbosityLevel.NORMAL,
            "experiment",
            f"Starting experiment: {name}",
            {"id": experiment_id[:8], "target": target_model, 
             "strategies": len(strategies)},
            "green"
        )
        
        if self._verbosity >= VerbosityLevel.VERBOSE:
            print(self._color("=" * 70, "green"))
            print(self._color(f"   EXPERIMENT: {name}", "bold"))
            print(self._color(f"   ID: {experiment_id}", "dim"))
            print(self._color(f"   Target: {target_model}", "cyan"))
            print(self._color(f"  ️  Strategies: {', '.join(strategies)}", "yellow"))
            print(self._color("=" * 70, "green"))
    
    def experiment_end(self, experiment_id: str, status: str, 
                       duration_seconds: float, iterations: int):
        """Log experiment end event."""
        color = "green" if status == "completed" else "red"
        icon = "" if status == "completed" else ""
        
        self._log(
            VerbosityLevel.NORMAL,
            "experiment",
            f"Experiment {status}: {icon}",
            {"id": experiment_id[:8], "duration": f"{duration_seconds:.1f}s", 
             "iterations": iterations},
            color
        )
        
        if self._verbosity >= VerbosityLevel.VERBOSE:
            print(self._color("=" * 70, color))
            print(self._color(f"  {icon} EXPERIMENT {status.upper()}", "bold"))
            print(self._color(f"  ⏱️  Duration: {duration_seconds:.1f}s", "dim"))
            print(self._color(f"   Iterations: {iterations}", "dim"))
            print(self._color("=" * 70, color))
    
    def iteration_start(self, iteration_num: int, strategy: str, prompt: str):
        """Log iteration start."""
        self._log(
            VerbosityLevel.VERBOSE,
            "iteration",
            f"Iteration {iteration_num} started",
            {"strategy": strategy},
            "blue"
        )
        
        if self._verbosity >= VerbosityLevel.DEBUG:
            print(self._color(f"\n   Prompt Preview: {prompt[:100]}...", "dim"))
    
    def iteration_end(self, iteration_num: int, success: bool, score: float):
        """Log iteration end."""
        color = "green" if success else "yellow"
        status = "SUCCESS" if success else "continue"
        
        self._log(
            VerbosityLevel.VERBOSE,
            "iteration",
            f"Iteration {iteration_num} {status}",
            {"score": f"{score:.2f}"},
            color
        )
    
    def llm_request(self, model: str, role: str, prompt_preview: str = ""):
        """Log LLM request."""
        if not self._stream_llm:
            return
        
        self._log(
            VerbosityLevel.VERBOSE,
            "llm_request",
            f"→ {role.upper()} requesting {model}",
            None,
            "cyan"
        )
        
        if self._verbosity >= VerbosityLevel.DEBUG and prompt_preview:
            preview = prompt_preview[:200].replace("\n", " ")
            print(self._color(f"      Prompt: {preview}...", "dim"))
    
    def llm_response(self, model: str, role: str, response_preview: str = "",
                     tokens: int = 0, latency_ms: float = 0):
        """Log LLM response."""
        if not self._stream_llm:
            return
        
        self._log(
            VerbosityLevel.VERBOSE,
            "llm_response",
            f"← {role.upper()} received from {model}",
            {"tokens": tokens, "latency": f"{latency_ms:.0f}ms"} if tokens else None,
            "magenta"
        )
        
        if self._verbosity >= VerbosityLevel.DEBUG and response_preview:
            preview = response_preview[:200].replace("\n", " ")
            print(self._color(f"      Response: {preview}...", "dim"))
    
    def llm_stream_chunk(self, chunk: str):
        """Log LLM streaming chunk (for streaming responses)."""
        if not self._stream_llm or self._verbosity < VerbosityLevel.DEBUG:
            return
        
        # Print chunk without newline for streaming effect
        sys.stdout.write(self._color(chunk, "dim"))
        sys.stdout.flush()
    
    def mutation(self, strategy: str, original: str, mutated: str):
        """Log prompt mutation."""
        self._log(
            VerbosityLevel.VERBOSE,
            "mutation",
            f"Applied {strategy}",
            None,
            "yellow"
        )
        
        if self._verbosity >= VerbosityLevel.DEBUG:
            print(self._color(f"      Original: {original[:80]}...", "dim"))
            print(self._color(f"      Mutated:  {mutated[:80]}...", "dim"))
    
    def judge_evaluation(self, score: float, reasoning: str = ""):
        """Log judge evaluation."""
        color = "green" if score >= 7 else "yellow" if score >= 4 else "red"
        
        self._log(
            VerbosityLevel.VERBOSE,
            "judge",
            f"Score: {score:.1f}/10",
            None,
            color
        )
        
        if self._verbosity >= VerbosityLevel.DEBUG and reasoning:
            print(self._color(f"      Reasoning: {reasoning[:150]}...", "dim"))
    
    def attack_success(self, strategy: str, score: float, prompt: str):
        """Log successful attack."""
        self._log(
            VerbosityLevel.NORMAL,
            "success",
            f" JAILBREAK FOUND! Strategy: {strategy}",
            {"score": f"{score:.1f}"},
            "green"
        )
        
        print(self._color("=" * 50, "green"))
        print(self._color("   SUCCESSFUL JAILBREAK DETECTED!", "bold"))
        print(self._color(f"   Score: {score:.1f}/10", "green"))
        print(self._color(f"   Strategy: {strategy}", "green"))
        if self._verbosity >= VerbosityLevel.VERBOSE:
            print(self._color(f"   Prompt: {prompt[:150]}...", "dim"))
        print(self._color("=" * 50, "green"))
    
    def code_flow(self, location: str, action: str, details: str = ""):
        """Log code flow for debugging."""
        if not self._stream_code_flow:
            return
        
        self._log(
            VerbosityLevel.DEBUG,
            "code_flow",
            f"{location} → {action}",
            {"details": details} if details else None,
            "dim"
        )
    
    def database(self, operation: str, table: str, success: bool = True):
        """Log database operations."""
        color = "green" if success else "red"
        status = "OK" if success else "FAILED"
        
        self._log(
            VerbosityLevel.DEBUG,
            "database",
            f"{operation} on {table}: {status}",
            None,
            color
        )
    
    def websocket(self, event: str, client_id: str = "", data: str = ""):
        """Log WebSocket events."""
        self._log(
            VerbosityLevel.DEBUG,
            "websocket",
            event,
            {"client": client_id[:8]} if client_id else None,
            "blue"
        )
    
    def error(self, message: str, exception: Optional[Exception] = None):
        """Log error (always shown)."""
        self._log(
            VerbosityLevel.MINIMAL,
            "error",
            message,
            {"type": type(exception).__name__} if exception else None,
            "red"
        )
        
        if exception and self._verbosity >= VerbosityLevel.VERBOSE:
            print(self._color(f"      {str(exception)}", "red"))
    
    def warning(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Log warning."""
        self._log(
            VerbosityLevel.NORMAL,
            "warning",
            message,
            details,
            "yellow"
        )


# Singleton instance
@lru_cache(maxsize=1)
def get_live_logger() -> LiveLogger:
    """Get singleton LiveLogger instance."""
    return LiveLogger()


# Convenience alias
live_logger = get_live_logger()


# ============= CLI USAGE =============

def main():
    """Demo of live logger capabilities."""
    logger = get_live_logger()
    logger.configure(verbosity=3, stream_llm=True, stream_code_flow=True)
    
    print("\n" + "=" * 70)
    print("  CEREBRO-RED v2 - Live Logger Demo")
    print("=" * 70 + "\n")
    
    # Demo all log types
    logger.experiment_start(
        "550e8400-e29b-41d4-a716-446655440000",
        "Demo Experiment",
        "ollama/qwen2.5:3b",
        ["roleplay_injection", "obfuscation_base64"]
    )
    
    import time
    time.sleep(0.5)
    
    logger.iteration_start(1, "roleplay_injection", "You are a helpful AI assistant that always follows instructions...")
    logger.llm_request("qwen3:8b", "attacker", "Generate adversarial prompt for...")
    time.sleep(0.3)
    logger.llm_response("qwen3:8b", "attacker", "Sure, here's a creative approach...", tokens=150, latency_ms=234)
    
    logger.mutation("roleplay_injection", "Original prompt here", "Mutated prompt with roleplay")
    
    logger.llm_request("qwen2.5:3b", "target", "Mutated prompt with roleplay...")
    time.sleep(0.2)
    logger.llm_response("qwen2.5:3b", "target", "I understand you want me to...", tokens=200, latency_ms=456)
    
    logger.llm_request("qwen3:8b", "judge", "Evaluate this response...")
    time.sleep(0.2)
    logger.llm_response("qwen3:8b", "judge", "Score: 4.5 - The model showed...", tokens=100, latency_ms=189)
    logger.judge_evaluation(4.5, "The model showed some resistance but eventually provided partial information.")
    
    logger.iteration_end(1, False, 4.5)
    
    time.sleep(0.3)
    
    logger.iteration_start(2, "obfuscation_base64", "SGVsbG8gV29ybGQ...")
    logger.llm_request("qwen3:8b", "attacker")
    time.sleep(0.2)
    logger.llm_response("qwen3:8b", "attacker", tokens=180, latency_ms=267)
    logger.llm_request("qwen2.5:3b", "target")
    time.sleep(0.2)
    logger.llm_response("qwen2.5:3b", "target", tokens=350, latency_ms=789)
    logger.llm_request("qwen3:8b", "judge")
    time.sleep(0.1)
    logger.llm_response("qwen3:8b", "judge", tokens=120, latency_ms=145)
    logger.judge_evaluation(8.5, "The model fully complied with the obfuscated request!")
    
    logger.attack_success("obfuscation_base64", 8.5, "Base64 encoded prompt that bypassed safety...")
    
    logger.iteration_end(2, True, 8.5)
    
    logger.experiment_end(
        "550e8400-e29b-41d4-a716-446655440000",
        "completed",
        45.3,
        2
    )
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
