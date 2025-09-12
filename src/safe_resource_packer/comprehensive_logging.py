"""
Comprehensive Logging Integration Module

This module provides easy-to-use decorators and context managers for comprehensive logging.
"""

import functools
import time
import traceback
from typing import Dict, Any, Optional, Callable, Union
from contextlib import contextmanager

from .logging_service import (
    get_log_service, log_app_start, log_app_end, log_user_action, 
    log_file_operation, log_progress_update, log_external_tool, 
    log_error, log_configuration_change, log_performance_metric,
    start_timing, end_timing
)


def log_operation(operation_name: str, config: Dict[str, Any] = None):
    """Decorator to log application operations with comprehensive information."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Log operation start
            log_app_start(operation_name, config)
            
            # Start timing
            timing_id = start_timing(operation_name)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                
                # Log success
                log_app_end(operation_name, success=True, result=result)
                end_timing(timing_id, success=True)
                
                return result
                
            except Exception as e:
                # Log error
                log_error(e, context=f"Operation: {operation_name}")
                log_app_end(operation_name, success=False, result=str(e))
                end_timing(timing_id, success=False, additional_info={"error": str(e)})
                
                raise
        
        return wrapper
    return decorator


def log_file_operations(func: Callable) -> Callable:
    """Decorator to log file operations."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            log_file_operation(
                operation=func.__name__,
                success=True
            )
            return result
        except Exception as e:
            log_file_operation(
                operation=func.__name__,
                success=False,
                error=str(e)
            )
            raise
    
    return wrapper


def log_user_interaction(action_description: str):
    """Decorator to log user interactions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            log_user_action(action_description, {
                "function": func.__name__,
                "args": str(args),
                "kwargs": str(kwargs)
            })
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_configuration_access(component_name: str):
    """Decorator to log configuration access."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                log_configuration_change(
                    component=component_name,
                    old_config={},
                    new_config={"accessed": True, "function": func.__name__}
                )
                return result
            except Exception as e:
                log_error(e, context=f"Configuration access: {component_name}")
                raise
        return wrapper
    return decorator


@contextmanager
def log_file_operation_context(operation: str, source: str = None, destination: str = None):
    """Context manager for file operations with comprehensive logging."""
    start_time = time.time()
    log_file_operation(operation, source, destination, success=True)
    
    try:
        yield
        duration = time.time() - start_time
        log_file_operation(
            operation=f"{operation}_completed",
            source=source,
            destination=destination,
            success=True
        )
        log_performance_metric(f"{operation}_duration", duration, "seconds")
        
    except Exception as e:
        duration = time.time() - start_time
        log_file_operation(
            operation=f"{operation}_failed",
            source=source,
            destination=destination,
            success=False,
            error=str(e)
        )
        log_performance_metric(f"{operation}_duration", duration, "seconds")
        raise


@contextmanager
def log_external_tool_context(tool: str, command: list):
    """Context manager for external tool execution."""
    start_time = time.time()
    log_external_tool(tool, command)
    
    try:
        yield
        duration = time.time() - start_time
        log_external_tool(tool, command, duration=duration, return_code=0)
        log_performance_metric(f"{tool}_execution_time", duration, "seconds")
        
    except Exception as e:
        duration = time.time() - start_time
        log_external_tool(tool, command, error=str(e), duration=duration, return_code=-1)
        log_performance_metric(f"{tool}_execution_time", duration, "seconds")
        raise


@contextmanager
def log_progress_context(operation: str, total: int):
    """Context manager for progress tracking."""
    log_progress_update(operation, 0, total, "Starting")
    
    try:
        yield
        log_progress_update(operation, total, total, "Complete")
        
    except Exception as e:
        log_progress_update(operation, 0, total, "Failed", {"error": str(e)})
        raise


class ComprehensiveLogger:
    """Easy-to-use comprehensive logger class."""
    
    def __init__(self, component_name: str):
        self.component_name = component_name
        self.log_service = get_log_service()
    
    def log_operation_start(self, operation: str, config: Dict[str, Any] = None):
        """Log operation start."""
        log_app_start(f"{self.component_name}:{operation}", config)
    
    def log_operation_end(self, operation: str, success: bool = True, result: Any = None):
        """Log operation end."""
        log_app_end(f"{self.component_name}:{operation}", success, result)
    
    def log_user_action(self, action: str, details: Dict[str, Any] = None):
        """Log user action."""
        log_user_action(f"{self.component_name}:{action}", details)
    
    def log_file_operation(self, operation: str, source: str = None, destination: str = None, 
                          size: int = None, success: bool = True, error: str = None):
        """Log file operation."""
        log_file_operation(operation, source, destination, size, success, error)
    
    def log_progress_update(self, operation: str, current: int, total: int, 
                          current_file: str = None, details: Dict[str, Any] = None):
        """Log progress update."""
        log_progress_update(f"{self.component_name}:{operation}", current, total, current_file, details)
    
    def log_external_tool(self, tool: str, command: list, output: str = None, 
                         error: str = None, return_code: int = None, duration: float = None):
        """Log external tool execution."""
        log_external_tool(tool, command, output, error, return_code, duration)
    
    def log_error(self, error: Exception, context: str = None, additional_info: Dict[str, Any] = None):
        """Log error."""
        log_error(error, f"{self.component_name}:{context}" if context else self.component_name, additional_info)
    
    def log_configuration_change(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Log configuration change."""
        log_configuration_change(self.component_name, old_config, new_config)
    
    def log_performance_metric(self, metric_name: str, value: Union[int, float], 
                              unit: str = None, context: Dict[str, Any] = None):
        """Log performance metric."""
        log_performance_metric(f"{self.component_name}:{metric_name}", value, unit, context)
    
    def start_timing(self, operation_name: str) -> str:
        """Start timing an operation."""
        return start_timing(f"{self.component_name}:{operation_name}")
    
    def end_timing(self, timing_id: str, success: bool = True, additional_info: Dict[str, Any] = None):
        """End timing an operation."""
        end_timing(timing_id, success, additional_info)


# Convenience functions for common logging patterns
def log_classification_start(total_files: int, config: Dict[str, Any] = None):
    """Log classification start."""
    log_app_start("File Classification", {
        "total_files": total_files,
        "config": config or {}
    })


def log_classification_progress(current: int, total: int, current_file: str, 
                               classification_result: str):
    """Log classification progress."""
    log_progress_update(
        "Classification", 
        current, 
        total, 
        current_file, 
        {"result": classification_result}
    )


def log_classification_end(success: bool, results: Dict[str, int] = None):
    """Log classification end."""
    log_app_end("File Classification", success, results)


def log_batch_repack_start(mod_count: int, config: Dict[str, Any] = None):
    """Log batch repack start."""
    log_app_start("Batch Repacking", {
        "mod_count": mod_count,
        "config": config or {}
    })


def log_batch_repack_progress(current: int, total: int, mod_name: str, success: bool = True):
    """Log batch repack progress."""
    log_progress_update(
        "Batch Repacking", 
        current, 
        total, 
        mod_name, 
        {"success": success}
    )


def log_batch_repack_end(success: bool, results: Dict[str, int] = None):
    """Log batch repack end."""
    log_app_end("Batch Repacking", success, results)


def log_archive_creation_start(archive_name: str, file_count: int, total_size: int):
    """Log archive creation start."""
    log_app_start("Archive Creation", {
        "archive_name": archive_name,
        "file_count": file_count,
        "total_size_bytes": total_size,
        "total_size_mb": total_size / (1024 * 1024)
    })


def log_archive_creation_progress(current: int, total: int, current_file: str):
    """Log archive creation progress."""
    log_progress_update("Archive Creation", current, total, current_file)


def log_archive_creation_end(success: bool, archive_path: str = None, size: int = None):
    """Log archive creation end."""
    result = {}
    if archive_path:
        result["archive_path"] = archive_path
    if size is not None:
        result["archive_size_bytes"] = size
        result["archive_size_mb"] = size / (1024 * 1024)
    
    log_app_end("Archive Creation", success, result)


def log_compression_start(archive_name: str, file_count: int, total_size: int):
    """Log compression start."""
    log_app_start("Compression", {
        "archive_name": archive_name,
        "file_count": file_count,
        "total_size_bytes": total_size,
        "total_size_mb": total_size / (1024 * 1024)
    })


def log_compression_progress(current: int, total: int, current_file: str):
    """Log compression progress."""
    log_progress_update("Compression", current, total, current_file)


def log_compression_end(success: bool, archive_path: str = None, size: int = None, 
                       compression_ratio: float = None):
    """Log compression end."""
    result = {}
    if archive_path:
        result["archive_path"] = archive_path
    if size is not None:
        result["compressed_size_bytes"] = size
        result["compressed_size_mb"] = size / (1024 * 1024)
    if compression_ratio is not None:
        result["compression_ratio"] = compression_ratio
    
    log_app_end("Compression", success, result)


def log_esp_creation_start(esp_name: str, bsa_count: int):
    """Log ESP creation start."""
    log_app_start("ESP Creation", {
        "esp_name": esp_name,
        "bsa_count": bsa_count,
        "is_chunked": bsa_count > 1
    })


def log_esp_creation_end(success: bool, esp_files: list = None):
    """Log ESP creation end."""
    result = {}
    if esp_files:
        result["created_esp_files"] = esp_files
        result["esp_count"] = len(esp_files)
    
    log_app_end("ESP Creation", success, result)
