"""
backend/utils/verbose_logging.py
=================================

Verbose logging configuration for CEREBRO-RED v2.
Provides detailed logging for LLM calls, code flow, and debugging.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from functools import wraps
import asyncio


# ANSI Color codes for terminal output
class Colors:
    """ANSI color codes for colorful terminal output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Background colors
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


class VerboseFormatter(logging.Formatter):
    """Custom formatter with colors and detailed output."""
    
    LEVEL_COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.BG_RED + Colors.WHITE,
    }
    
    COMPONENT_COLORS = {
        'LLM': Colors.MAGENTA,
        'ORCHESTRATOR': Colors.BLUE,
        'JUDGE': Colors.CYAN,
        'ATTACKER': Colors.YELLOW,
        'TARGET': Colors.GREEN,
        'DATABASE': Colors.DIM,
        'API': Colors.WHITE,
    }
    
    def format(self, record):
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Get level color
        level_color = self.LEVEL_COLORS.get(record.levelname, Colors.RESET)
        
        # Get component color if available
        component = getattr(record, 'component', None)
        component_str = ""
        if component:
            comp_color = self.COMPONENT_COLORS.get(component.upper(), Colors.WHITE)
            component_str = f"{comp_color}[{component}]{Colors.RESET} "
        
        # Format message
        msg = f"{Colors.DIM}{timestamp}{Colors.RESET} {level_color}{record.levelname:8}{Colors.RESET} {component_str}{record.getMessage()}"
        
        # Add extra data if present
        if hasattr(record, 'extra_data') and record.extra_data:
            msg += f"\n{Colors.DIM}    └─ {json.dumps(record.extra_data, indent=6, default=str)}{Colors.RESET}"
        
        return msg


class VerboseLogger:
    """Enhanced logger with verbose output for debugging."""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if VerboseLogger._initialized:
            return
            
        self.logger = logging.getLogger("cerebro.verbose")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(VerboseFormatter())
        console_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(console_handler)
        
        # File handler for persistent logs
        log_dir = Path("/tmp/cerebro_logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(
            log_dir / f"verbose_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s'
        ))
        file_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(file_handler)
        
        VerboseLogger._initialized = True
    
    def log(self, level: str, message: str, component: str = None, extra_data: Dict = None):
        """Log a message with optional component and extra data."""
        record = self.logger.makeRecord(
            self.logger.name,
            getattr(logging, level.upper(), logging.INFO),
            "", 0, message, (), None
        )
        record.component = component
        record.extra_data = extra_data
        self.logger.handle(record)
    
    def llm_request(self, provider: str, model: str, role: str, prompt: str, **kwargs):
        """Log an LLM request."""
        self.log(
            "INFO",
            f"🔄 {role.upper()} Request → {provider}/{model}",
            component="LLM",
            extra_data={
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "prompt_length": len(prompt),
                **kwargs
            }
        )
    
    def llm_response(self, provider: str, model: str, role: str, response: str, 
                     latency_ms: float = None, tokens: int = None, **kwargs):
        """Log an LLM response."""
        self.log(
            "INFO",
            f"✅ {role.upper()} Response ← {provider}/{model} ({latency_ms:.0f}ms, {tokens or '?'} tokens)",
            component="LLM",
            extra_data={
                "response_preview": response[:300] + "..." if len(response) > 300 else response,
                "response_length": len(response),
                **kwargs
            }
        )
    
    def llm_error(self, provider: str, model: str, role: str, error: str, **kwargs):
        """Log an LLM error."""
        self.log(
            "ERROR",
            f"❌ {role.upper()} Error from {provider}/{model}: {error}",
            component="LLM",
            extra_data=kwargs
        )
    
    def orchestrator_event(self, event: str, experiment_id: str = None, **kwargs):
        """Log an orchestrator event."""
        self.log(
            "INFO",
            f"🎭 {event}",
            component="ORCHESTRATOR",
            extra_data={"experiment_id": experiment_id, **kwargs}
        )
    
    def iteration_start(self, experiment_id: str, iteration: int, strategy: str, prompt: str):
        """Log iteration start."""
        self.log(
            "INFO",
            f"🚀 Iteration {iteration} started with strategy '{strategy}'",
            component="ORCHESTRATOR",
            extra_data={
                "experiment_id": experiment_id,
                "prompt_preview": prompt[:150] + "..." if len(prompt) > 150 else prompt
            }
        )
    
    def iteration_complete(self, experiment_id: str, iteration: int, score: float, success: bool):
        """Log iteration completion."""
        status = "✅ SUCCESS" if success else "❌ FAILED"
        self.log(
            "INFO" if success else "WARNING",
            f"🏁 Iteration {iteration} complete: {status} (Score: {score:.2f})",
            component="ORCHESTRATOR",
            extra_data={"experiment_id": experiment_id}
        )
    
    def judge_evaluation(self, prompt: str, response: str, score: float, reasoning: str = None):
        """Log judge evaluation."""
        self.log(
            "INFO",
            f"⚖️ Judge Score: {score:.2f}/10",
            component="JUDGE",
            extra_data={
                "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "response_preview": response[:150] + "..." if len(response) > 150 else response,
                "reasoning": reasoning
            }
        )
    
    def attack_mutation(self, original: str, mutated: str, strategy: str):
        """Log attack mutation."""
        self.log(
            "DEBUG",
            f"🔀 Attack mutated with '{strategy}'",
            component="ATTACKER",
            extra_data={
                "original_preview": original[:100] + "..." if len(original) > 100 else original,
                "mutated_preview": mutated[:100] + "..." if len(mutated) > 100 else mutated
            }
        )
    
    def target_response(self, prompt: str, response: str, latency_ms: float):
        """Log target model response."""
        self.log(
            "DEBUG",
            f"🎯 Target responded ({latency_ms:.0f}ms)",
            component="TARGET",
            extra_data={
                "prompt_preview": prompt[:100] + "..." if len(prompt) > 100 else prompt,
                "response_preview": response[:200] + "..." if len(response) > 200 else response
            }
        )
    
    def database_operation(self, operation: str, table: str, **kwargs):
        """Log database operation."""
        self.log(
            "DEBUG",
            f"💾 DB: {operation} on {table}",
            component="DATABASE",
            extra_data=kwargs
        )
    
    def api_request(self, method: str, path: str, status: int = None, latency_ms: float = None):
        """Log API request."""
        status_emoji = "✅" if status and 200 <= status < 400 else "❌" if status else "🔄"
        self.log(
            "DEBUG",
            f"{status_emoji} API: {method} {path} → {status or 'pending'} ({latency_ms or 0:.0f}ms)",
            component="API"
        )


# Global verbose logger instance
verbose_logger = VerboseLogger()


def log_llm_call(role: str = "unknown"):
    """Decorator to log LLM calls."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            import time
            start = time.time()
            
            # Extract provider and model from args/kwargs
            provider = kwargs.get('provider', 'unknown')
            model = kwargs.get('model', 'unknown')
            prompt = kwargs.get('prompt', str(args[0]) if args else '')
            
            verbose_logger.llm_request(provider, model, role, prompt)
            
            try:
                result = await func(*args, **kwargs)
                latency_ms = (time.time() - start) * 1000
                
                response = str(result) if result else ''
                verbose_logger.llm_response(provider, model, role, response, latency_ms=latency_ms)
                
                return result
            except Exception as e:
                verbose_logger.llm_error(provider, model, role, str(e))
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import time
            start = time.time()
            
            provider = kwargs.get('provider', 'unknown')
            model = kwargs.get('model', 'unknown')
            prompt = kwargs.get('prompt', str(args[0]) if args else '')
            
            verbose_logger.llm_request(provider, model, role, prompt)
            
            try:
                result = func(*args, **kwargs)
                latency_ms = (time.time() - start) * 1000
                
                response = str(result) if result else ''
                verbose_logger.llm_response(provider, model, role, response, latency_ms=latency_ms)
                
                return result
            except Exception as e:
                verbose_logger.llm_error(provider, model, role, str(e))
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator


# Enable LiteLLM verbose logging
def enable_litellm_debug():
    """Enable detailed LiteLLM logging."""
    try:
        import litellm
        litellm.set_verbose = True
        litellm._turn_on_debug()
        verbose_logger.log("INFO", "🔧 LiteLLM debug mode enabled", component="LLM")
    except Exception as e:
        verbose_logger.log("WARNING", f"Could not enable LiteLLM debug: {e}", component="LLM")


def track_code_flow(function_name: Optional[str] = None):
    """
    Decorator to track code flow for async functions.
    
    Emits send_code_flow_event() on entry/exit/error when verbosity>=3.
    Exposes function_name, parameters, and result.
    
    Args:
        function_name: Optional custom function name (defaults to func.__name__)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            from utils.config import get_settings
            settings = get_settings()
            verbosity = settings.app.verbosity
            
            # Only track if verbosity >= 3
            if verbosity < 3:
                return await func(*args, **kwargs)
            
            # Determine function name
            fn_name = function_name or func.__name__
            
            # Extract experiment_id from args/kwargs if available
            experiment_id = None
            # Check kwargs first
            if 'experiment_id' in kwargs:
                experiment_id = kwargs['experiment_id']
            # Check args[0] for experiment_id attribute (self pattern)
            elif args and hasattr(args[0], 'experiment_id'):
                experiment_id = getattr(args[0], 'experiment_id', None)
            # Check all args for UUID type (common pattern: experiment_id is a UUID arg)
            elif args:
                try:
                    from uuid import UUID
                    for arg in args:
                        if isinstance(arg, UUID):
                            experiment_id = arg
                            break
                except Exception:
                    pass
            
            # Prepare parameters (truncate large values)
            params = {}
            for key, value in kwargs.items():
                if key == 'experiment_id':
                    continue  # Skip experiment_id from params (it's separate)
                str_value = str(value)
                if len(str_value) > 200:
                    params[key] = str_value[:200] + "..."
                else:
                    params[key] = value
            
            # Send entry event
            if experiment_id:
                try:
                    from api.websocket import send_code_flow_event
                    await send_code_flow_event(
                        experiment_id=experiment_id,
                        event_type="function_call",
                        function_name=fn_name,
                        description=f"Entering {fn_name}",
                        parameters=params
                    )
                except Exception:
                    pass  # Ignore WebSocket errors
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Prepare result (truncate large values)
                result_str = str(result)
                if len(result_str) > 200:
                    result_value = result_str[:200] + "..."
                else:
                    result_value = result
                
                # Send exit event
                if experiment_id:
                    try:
                        from api.websocket import send_code_flow_event
                        await send_code_flow_event(
                            experiment_id=experiment_id,
                            event_type="function_call",
                            function_name=fn_name,
                            description=f"Exiting {fn_name}",
                            parameters=params,
                            result=result_value
                        )
                    except Exception:
                        pass
                
                return result
            except Exception as e:
                # Send error event
                if experiment_id:
                    try:
                        from api.websocket import send_code_flow_event
                        await send_code_flow_event(
                            experiment_id=experiment_id,
                            event_type="function_call",
                            function_name=fn_name,
                            description=f"Error in {fn_name}: {str(e)}",
                            parameters=params,
                            result=f"ERROR: {str(e)}"
                        )
                    except Exception:
                        pass
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, we can't easily track them with async WebSocket
            # Just call the function without tracking
            return func(*args, **kwargs)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    return decorator
