"""
Ultra-Comprehensive Logging Service for Safe Resource Packer

This service provides maximum information capture for debugging user issues.
Logs are stored in the user's chosen output folder with detailed context.
"""

import os
import sys
import time
import json
import traceback
import platform
import psutil
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler


class ComprehensiveLogService:
    """Ultra-comprehensive logging service for maximum debugging information."""
    
    def __init__(self, output_dir: str, session_name: str = None):
        """
        Initialize the comprehensive logging service.
        
        Args:
            output_dir: Directory where logs will be stored
            session_name: Optional session identifier
        """
        self.output_dir = Path(output_dir)
        self.session_name = session_name or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.session_start = datetime.now()
        
        # Create logs directory
        self.logs_dir = self.output_dir / "logs" / self.session_name
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize loggers
        self._setup_loggers()
        
        # Session metadata
        self.session_metadata = self._capture_system_info()
        self._log_session_start()
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Performance tracking
        self.performance_data = {}
        self.operation_timings = {}
        
    def _setup_loggers(self):
        """Setup multiple specialized loggers for different types of information."""
        
        # Main application logger
        self.app_logger = self._create_logger(
            "app", 
            self.logs_dir / "application.log",
            level=logging.DEBUG
        )
        
        # System information logger
        self.system_logger = self._create_logger(
            "system",
            self.logs_dir / "system.log", 
            level=logging.INFO
        )
        
        # Performance logger
        self.performance_logger = self._create_logger(
            "performance",
            self.logs_dir / "performance.log",
            level=logging.INFO
        )
        
        # Error logger (detailed errors with stack traces)
        self.error_logger = self._create_logger(
            "error",
            self.logs_dir / "errors.log",
            level=logging.ERROR
        )
        
        # User actions logger
        self.user_logger = self._create_logger(
            "user",
            self.logs_dir / "user_actions.log",
            level=logging.INFO
        )
        
        # File operations logger
        self.file_logger = self._create_logger(
            "file_ops",
            self.logs_dir / "file_operations.log",
            level=logging.DEBUG
        )
        
        # Configuration logger
        self.config_logger = self._create_logger(
            "config",
            self.logs_dir / "configuration.log",
            level=logging.INFO
        )
        
        # Progress logger
        self.progress_logger = self._create_logger(
            "progress",
            self.logs_dir / "progress.log",
            level=logging.INFO
        )
        
        # External tools logger (BSArch, 7z, etc.)
        self.tools_logger = self._create_logger(
            "tools",
            self.logs_dir / "external_tools.log",
            level=logging.DEBUG
        )
        
    def _create_logger(self, name: str, log_file: Path, level: int = logging.INFO) -> logging.Logger:
        """Create a logger with file rotation."""
        logger = logging.getLogger(f"srp_{name}")
        logger.setLevel(level)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Create rotating file handler (10MB max, keep 5 files)
        handler = RotatingFileHandler(
            log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(threadName)-10s | %(funcName)-20s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.propagate = False  # Don't propagate to root logger
        
        return logger
        
    def _capture_system_info(self) -> Dict[str, Any]:
        """Capture comprehensive system information."""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "platform": {
                    "system": platform.system(),
                    "release": platform.release(),
                    "version": platform.version(),
                    "machine": platform.machine(),
                    "processor": platform.processor(),
                    "python_version": platform.python_version(),
                    "python_implementation": platform.python_implementation(),
                },
                "environment": {
                    "python_path": sys.executable,
                    "working_directory": os.getcwd(),
                    "environment_variables": dict(os.environ),
                },
                "system_resources": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total,
                    "memory_available": psutil.virtual_memory().available,
                    "disk_usage": psutil.disk_usage('/')._asdict() if os.name != 'nt' else psutil.disk_usage('C:')._asdict(),
                },
                "application": {
                    "session_name": self.session_name,
                    "session_start": self.session_start.isoformat(),
                    "log_directory": str(self.logs_dir),
                }
            }
        except Exception as e:
            return {"error": f"Failed to capture system info: {e}"}
    
    def _log_session_start(self):
        """Log session start with comprehensive information."""
        self.system_logger.info("=" * 80)
        self.system_logger.info("SAFE RESOURCE PACKER SESSION STARTED")
        self.system_logger.info("=" * 80)
        
        # Log system information
        self.system_logger.info(f"Session: {self.session_name}")
        self.system_logger.info(f"Start Time: {self.session_start}")
        self.system_logger.info(f"Log Directory: {self.logs_dir}")
        
        # Log platform info
        self.system_logger.info(f"Platform: {platform.system()} {platform.release()}")
        self.system_logger.info(f"Python: {platform.python_version()} ({platform.python_implementation()})")
        self.system_logger.info(f"Architecture: {platform.machine()}")
        
        # Log system resources
        try:
            memory = psutil.virtual_memory()
            self.system_logger.info(f"Memory: {memory.total // (1024**3)}GB total, {memory.available // (1024**3)}GB available")
            self.system_logger.info(f"CPU Cores: {psutil.cpu_count()}")
        except Exception as e:
            self.system_logger.warning(f"Could not get system resources: {e}")
        
        # Save session metadata to JSON
        metadata_file = self.logs_dir / "session_metadata.json"
        try:
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_metadata, f, indent=2, ensure_ascii=False)
            self.system_logger.info(f"Session metadata saved to: {metadata_file}")
        except Exception as e:
            self.system_logger.error(f"Failed to save session metadata: {e}")
    
    def log_application_start(self, operation: str, config: Dict[str, Any] = None):
        """Log application operation start."""
        with self._lock:
            self.app_logger.info("=" * 60)
            self.app_logger.info(f"OPERATION STARTED: {operation}")
            self.app_logger.info("=" * 60)
            
            if config:
                self.config_logger.info(f"Configuration for {operation}:")
                self.config_logger.info(json.dumps(config, indent=2, ensure_ascii=False))
            
            # Start performance tracking
            self.performance_data[operation] = {
                "start_time": time.time(),
                "start_datetime": datetime.now().isoformat(),
                "config": config or {}
            }
    
    def log_application_end(self, operation: str, success: bool = True, result: Any = None):
        """Log application operation end."""
        with self._lock:
            if operation in self.performance_data:
                end_time = time.time()
                duration = end_time - self.performance_data[operation]["start_time"]
                
                self.app_logger.info("=" * 60)
                self.app_logger.info(f"OPERATION COMPLETED: {operation}")
                self.app_logger.info(f"Success: {success}")
                self.app_logger.info(f"Duration: {duration:.2f} seconds")
                self.app_logger.info("=" * 60)
                
                # Log performance data
                self.performance_logger.info(f"Operation: {operation}")
                self.performance_logger.info(f"Duration: {duration:.2f}s")
                self.performance_logger.info(f"Success: {success}")
                
                if result:
                    self.app_logger.info(f"Result: {result}")
                
                # Update performance data
                self.performance_data[operation].update({
                    "end_time": end_time,
                    "duration": duration,
                    "success": success,
                    "result": str(result) if result else None
                })
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user actions for debugging user behavior."""
        with self._lock:
            self.user_logger.info(f"USER ACTION: {action}")
            if details:
                self.user_logger.info(f"Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
    
    def log_file_operation(self, operation: str, source: str = None, destination: str = None, 
                          size: int = None, success: bool = True, error: str = None):
        """Log detailed file operations."""
        with self._lock:
            self.file_logger.info(f"FILE {operation.upper()}: {success}")
            if source:
                self.file_logger.info(f"Source: {source}")
            if destination:
                self.file_logger.info(f"Destination: {destination}")
            if size is not None:
                self.file_logger.info(f"Size: {size} bytes ({size / (1024*1024):.2f} MB)")
            if error:
                self.file_logger.error(f"Error: {error}")
    
    def log_progress_update(self, operation: str, current: int, total: int, 
                          current_file: str = None, details: Dict[str, Any] = None):
        """Log progress updates."""
        with self._lock:
            percentage = (current / total * 100) if total > 0 else 0
            self.progress_logger.info(f"PROGRESS: {operation} - {current}/{total} ({percentage:.1f}%)")
            if current_file:
                self.progress_logger.info(f"Current file: {current_file}")
            if details:
                self.progress_logger.info(f"Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
    
    def log_external_tool(self, tool: str, command: List[str], output: str = None, 
                         error: str = None, return_code: int = None, duration: float = None):
        """Log external tool execution (BSArch, 7z, etc.)."""
        with self._lock:
            self.tools_logger.info(f"EXTERNAL TOOL: {tool}")
            self.tools_logger.info(f"Command: {' '.join(command)}")
            if return_code is not None:
                self.tools_logger.info(f"Return code: {return_code}")
            if duration is not None:
                self.tools_logger.info(f"Duration: {duration:.2f}s")
            if output:
                self.tools_logger.info(f"Output: {output}")
            if error:
                self.tools_logger.error(f"Error: {error}")
    
    def log_error(self, error: Exception, context: str = None, additional_info: Dict[str, Any] = None):
        """Log detailed error information with stack trace."""
        with self._lock:
            self.error_logger.error("=" * 60)
            self.error_logger.error(f"ERROR OCCURRED: {type(error).__name__}")
            self.error_logger.error("=" * 60)
            
            if context:
                self.error_logger.error(f"Context: {context}")
            
            self.error_logger.error(f"Error message: {str(error)}")
            
            # Log full stack trace
            self.error_logger.error("Stack trace:")
            for line in traceback.format_exc().splitlines():
                self.error_logger.error(line)
            
            if additional_info:
                self.error_logger.error(f"Additional info: {json.dumps(additional_info, indent=2, ensure_ascii=False)}")
            
            self.error_logger.error("=" * 60)
    
    def log_configuration_change(self, component: str, old_config: Dict[str, Any], 
                               new_config: Dict[str, Any]):
        """Log configuration changes."""
        with self._lock:
            self.config_logger.info(f"CONFIGURATION CHANGE: {component}")
            self.config_logger.info("Old configuration:")
            self.config_logger.info(json.dumps(old_config, indent=2, ensure_ascii=False))
            self.config_logger.info("New configuration:")
            self.config_logger.info(json.dumps(new_config, indent=2, ensure_ascii=False))
    
    def log_performance_metric(self, metric_name: str, value: Union[int, float], 
                              unit: str = None, context: Dict[str, Any] = None):
        """Log performance metrics."""
        with self._lock:
            self.performance_logger.info(f"PERFORMANCE METRIC: {metric_name}")
            self.performance_logger.info(f"Value: {value}")
            if unit:
                self.performance_logger.info(f"Unit: {unit}")
            if context:
                self.performance_logger.info(f"Context: {json.dumps(context, indent=2, ensure_ascii=False)}")
    
    def start_operation_timing(self, operation_name: str) -> str:
        """Start timing an operation and return timing ID."""
        timing_id = f"{operation_name}_{int(time.time() * 1000)}"
        self.operation_timings[timing_id] = {
            "operation": operation_name,
            "start_time": time.time(),
            "start_datetime": datetime.now().isoformat()
        }
        return timing_id
    
    def end_operation_timing(self, timing_id: str, success: bool = True, 
                           additional_info: Dict[str, Any] = None):
        """End timing an operation."""
        if timing_id in self.operation_timings:
            end_time = time.time()
            timing_data = self.operation_timings[timing_id]
            duration = end_time - timing_data["start_time"]
            
            timing_data.update({
                "end_time": end_time,
                "duration": duration,
                "success": success,
                "additional_info": additional_info or {}
            })
            
            self.performance_logger.info(f"OPERATION TIMING: {timing_data['operation']}")
            self.performance_logger.info(f"Duration: {duration:.3f}s")
            self.performance_logger.info(f"Success: {success}")
            if additional_info:
                self.performance_logger.info(f"Additional info: {json.dumps(additional_info, indent=2, ensure_ascii=False)}")
    
    def log_session_end(self):
        """Log session end with summary."""
        with self._lock:
            session_end = datetime.now()
            session_duration = (session_end - self.session_start).total_seconds()
            
            self.system_logger.info("=" * 80)
            self.system_logger.info("SAFE RESOURCE PACKER SESSION ENDED")
            self.system_logger.info("=" * 80)
            self.system_logger.info(f"Session: {self.session_name}")
            self.system_logger.info(f"Start: {self.session_start}")
            self.system_logger.info(f"End: {session_end}")
            self.system_logger.info(f"Duration: {session_duration:.2f} seconds")
            
            # Log performance summary
            if self.performance_data:
                self.system_logger.info("Performance Summary:")
                for operation, data in self.performance_data.items():
                    self.system_logger.info(f"  {operation}: {data.get('duration', 0):.2f}s ({'SUCCESS' if data.get('success') else 'FAILED'})")
            
            # Save final session summary
            summary_file = self.logs_dir / "session_summary.json"
            try:
                summary_data = {
                    "session_name": self.session_name,
                    "start_time": self.session_start.isoformat(),
                    "end_time": session_end.isoformat(),
                    "duration_seconds": session_duration,
                    "performance_data": self.performance_data,
                    "operation_timings": self.operation_timings
                }
                
                with open(summary_file, 'w', encoding='utf-8') as f:
                    json.dump(summary_data, f, indent=2, ensure_ascii=False)
                
                self.system_logger.info(f"Session summary saved to: {summary_file}")
            except Exception as e:
                self.system_logger.error(f"Failed to save session summary: {e}")
    
    def get_log_directory(self) -> str:
        """Get the log directory path."""
        return str(self.logs_dir)
    
    def get_session_name(self) -> str:
        """Get the session name."""
        return self.session_name


# Global log service instance
_global_log_service: Optional[ComprehensiveLogService] = None


def initialize_logging(output_dir: str, session_name: str = None) -> ComprehensiveLogService:
    """Initialize the global logging service."""
    global _global_log_service
    _global_log_service = ComprehensiveLogService(output_dir, session_name)
    return _global_log_service


def get_log_service() -> Optional[ComprehensiveLogService]:
    """Get the global logging service instance."""
    return _global_log_service


def log_app_start(operation: str, config: Dict[str, Any] = None):
    """Log application operation start."""
    if _global_log_service:
        _global_log_service.log_application_start(operation, config)


def log_app_end(operation: str, success: bool = True, result: Any = None):
    """Log application operation end."""
    if _global_log_service:
        _global_log_service.log_application_end(operation, success, result)


def log_user_action(action: str, details: Dict[str, Any] = None):
    """Log user actions."""
    if _global_log_service:
        _global_log_service.log_user_action(action, details)


def log_file_operation(operation: str, source: str = None, destination: str = None, 
                      size: int = None, success: bool = True, error: str = None):
    """Log file operations."""
    if _global_log_service:
        _global_log_service.log_file_operation(operation, source, destination, size, success, error)


def log_progress_update(operation: str, current: int, total: int, 
                       current_file: str = None, details: Dict[str, Any] = None):
    """Log progress updates."""
    if _global_log_service:
        _global_log_service.log_progress_update(operation, current, total, current_file, details)


def log_external_tool(tool: str, command: List[str], output: str = None, 
                     error: str = None, return_code: int = None, duration: float = None):
    """Log external tool execution."""
    if _global_log_service:
        _global_log_service.log_external_tool(tool, command, output, error, return_code, duration)


def log_error(error: Exception, context: str = None, additional_info: Dict[str, Any] = None):
    """Log detailed errors."""
    if _global_log_service:
        _global_log_service.log_error(error, context, additional_info)


def log_configuration_change(component: str, old_config: Dict[str, Any], 
                           new_config: Dict[str, Any]):
    """Log configuration changes."""
    if _global_log_service:
        _global_log_service.log_configuration_change(component, old_config, new_config)


def log_performance_metric(metric_name: str, value: Union[int, float], 
                          unit: str = None, context: Dict[str, Any] = None):
    """Log performance metrics."""
    if _global_log_service:
        _global_log_service.log_performance_metric(metric_name, value, unit, context)


def start_timing(operation_name: str) -> str:
    """Start timing an operation."""
    if _global_log_service:
        return _global_log_service.start_operation_timing(operation_name)
    return ""


def end_timing(timing_id: str, success: bool = True, additional_info: Dict[str, Any] = None):
    """End timing an operation."""
    if _global_log_service:
        _global_log_service.end_operation_timing(timing_id, success, additional_info)


def log_session_end():
    """Log session end."""
    if _global_log_service:
        _global_log_service.log_session_end()
