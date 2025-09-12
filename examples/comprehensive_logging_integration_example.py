"""
Comprehensive Logging Integration Example

This example shows how to integrate the comprehensive logging system
into existing Safe Resource Packer components.
"""

import os
import sys
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from safe_resource_packer.logging_service import initialize_logging
from safe_resource_packer.comprehensive_logging import (
    log_operation, log_file_operations, log_user_interaction,
    ComprehensiveLogger, log_classification_start, log_classification_end,
    log_archive_creation_start, log_archive_creation_end,
    log_batch_repack_start, log_batch_repack_end,
    log_compression_start, log_compression_end
)


def example_classification_with_logging():
    """Example of how to add comprehensive logging to classification."""
    
    # Initialize logging (this would be done once at application start)
    output_dir = tempfile.mkdtemp()
    log_service = initialize_logging(output_dir, 'classification_example')
    
    print("=== CLASSIFICATION WITH COMPREHENSIVE LOGGING ===")
    
    # Log classification start
    log_classification_start(1000, {
        'source_path': '/path/to/mod',
        'game_type': 'skyrim',
        'classification_rules': 'default'
    })
    
    # Simulate classification process
    pack_count = 0
    loose_count = 0
    skip_count = 0
    
    for i in range(1000):
        # Simulate file classification
        if i % 3 == 0:
            result = 'pack'
            pack_count += 1
        elif i % 3 == 1:
            result = 'loose'
            loose_count += 1
        else:
            result = 'skip'
            skip_count += 1
        
        # Log progress every 100 files
        if i % 100 == 0:
            from safe_resource_packer.comprehensive_logging import log_progress_update
            log_progress_update('Classification', i, 1000, f'file_{i}.dds', {'result': result})
    
    # Log classification end
    log_classification_end(True, {
        'pack': pack_count,
        'loose': loose_count,
        'skip': skip_count
    })
    
    print(f"Classification completed! Logs saved to: {log_service.get_log_directory()}")
    return log_service.get_log_directory()


def example_batch_repacking_with_logging():
    """Example of how to add comprehensive logging to batch repacking."""
    
    # Initialize logging
    output_dir = tempfile.mkdtemp()
    log_service = initialize_logging(output_dir, 'batch_repack_example')
    
    print("=== BATCH REPACKING WITH COMPREHENSIVE LOGGING ===")
    
    # Log batch repack start
    log_batch_repack_start(5, {
        'collection_path': '/path/to/collection',
        'output_path': '/path/to/output',
        'game_type': 'skyrim'
    })
    
    # Simulate batch repacking process
    mods = ['Mod1', 'Mod2', 'Mod3', 'Mod4', 'Mod5']
    successful_mods = 0
    failed_mods = 0
    
    for i, mod_name in enumerate(mods):
        # Log mod processing start
        from safe_resource_packer.comprehensive_logging import log_batch_repack_progress
        log_batch_repack_progress(i+1, len(mods), mod_name, True)
        
        # Simulate mod processing
        if i < 4:  # First 4 mods succeed
            successful_mods += 1
            # Log archive creation
            log_archive_creation_start(f'{mod_name}.bsa', 500, 1024*1024*100)  # 100MB
            log_archive_creation_end(True, f'/output/{mod_name}.bsa', 1024*1024*50)  # 50MB
            
            # Log compression
            log_compression_start(f'{mod_name}.7z', 1, 1024*1024*50)
            log_compression_end(True, f'/output/{mod_name}.7z', 1024*1024*25, 0.5)  # 50% compression
        else:  # Last mod fails
            failed_mods += 1
            log_batch_repack_progress(i+1, len(mods), mod_name, False)
    
    # Log batch repack end
    log_batch_repack_end(True, {
        'successful': successful_mods,
        'failed': failed_mods,
        'total': len(mods)
    })
    
    print(f"Batch repacking completed! Logs saved to: {log_service.get_log_directory()}")
    return log_service.get_log_directory()


def example_decorator_usage():
    """Example of using decorators for automatic logging."""
    
    # Initialize logging
    output_dir = tempfile.mkdtemp()
    log_service = initialize_logging(output_dir, 'decorator_example')
    
    print("=== DECORATOR USAGE EXAMPLE ===")
    
    # Example 1: Operation logging decorator
    @log_operation('File Processing', {'decorator_test': True})
    def process_files(file_list):
        """Process a list of files."""
        processed_count = 0
        for file_path in file_list:
            # Simulate file processing
            processed_count += 1
        return processed_count
    
    # Example 2: File operations decorator
    @log_file_operations
    def copy_file(source, destination):
        """Copy a file from source to destination."""
        # Simulate file copy
        return True
    
    # Example 3: User interaction decorator
    @log_user_interaction('User selected mod for processing')
    def select_mod(mod_name):
        """User selects a mod for processing."""
        return mod_name
    
    # Execute examples
    file_list = ['file1.txt', 'file2.txt', 'file3.txt']
    result = process_files(file_list)
    print(f"Processed {result} files")
    
    copy_result = copy_file('/source/file.txt', '/dest/file.txt')
    print(f"File copy result: {copy_result}")
    
    selected_mod = select_mod('TestMod')
    print(f"Selected mod: {selected_mod}")
    
    print(f"Decorator example completed! Logs saved to: {log_service.get_log_directory()}")
    return log_service.get_log_directory()


def example_comprehensive_logger():
    """Example of using ComprehensiveLogger class."""
    
    # Initialize logging
    output_dir = tempfile.mkdtemp()
    log_service = initialize_logging(output_dir, 'comprehensive_logger_example')
    
    print("=== COMPREHENSIVE LOGGER EXAMPLE ===")
    
    # Create logger for a specific component
    logger = ComprehensiveLogger('ArchiveCreator')
    
    # Log component operations
    logger.log_operation_start('Create Archive', {
        'archive_name': 'TestArchive.bsa',
        'file_count': 1000,
        'game_type': 'skyrim'
    })
    
    # Log file operations
    logger.log_file_operation('copy', '/source/texture.dds', '/temp/texture.dds', 1024*1024*10, True)
    logger.log_file_operation('copy', '/source/mesh.nif', '/temp/mesh.nif', 1024*1024*5, True)
    
    # Log external tool usage
    logger.log_external_tool('BSArch', ['BSArch.exe', 'pack', '/temp', '/output/TestArchive.bsa'], 
                            'Archive created successfully', None, 0, 12.5)
    
    # Log progress
    logger.log_progress_update('Archive Creation', 1000, 1000, 'Complete')
    
    # Log performance metric
    logger.log_performance_metric('archive_size', 1024*1024*50, 'bytes', {'compression_ratio': 0.8})
    
    # Log operation end
    logger.log_operation_end('Create Archive', True, {
        'archive_path': '/output/TestArchive.bsa',
        'file_count': 1000,
        'size_bytes': 1024*1024*50
    })
    
    print(f"Comprehensive logger example completed! Logs saved to: {log_service.get_log_directory()}")
    return log_service.get_log_directory()


def show_log_structure(log_dir):
    """Show the structure of created log files."""
    log_path = Path(log_dir)
    
    print(f"\n=== LOG STRUCTURE: {log_path.name} ===")
    print(f"Log directory: {log_path}")
    
    # Show log files
    log_files = sorted(log_path.glob('*.log'))
    if log_files:
        print("\nLog files:")
        for log_file in log_files:
            size = log_file.stat().st_size
            print(f"  • {log_file.name} ({size} bytes)")
    
    # Show JSON files
    json_files = sorted(log_path.glob('*.json'))
    if json_files:
        print("\nJSON files:")
        for json_file in json_files:
            size = json_file.stat().st_size
            print(f"  • {json_file.name} ({size} bytes)")
    
    # Show sample content from application.log
    app_log = log_path / 'application.log'
    if app_log.exists():
        print(f"\nSample from application.log:")
        with open(app_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:5]  # First 5 lines
            for line in lines:
                print(f"  {line.strip()}")


if __name__ == "__main__":
    print("COMPREHENSIVE LOGGING INTEGRATION EXAMPLES")
    print("=" * 50)
    
    # Run examples
    examples = [
        ("Classification", example_classification_with_logging),
        ("Batch Repacking", example_batch_repacking_with_logging),
        ("Decorators", example_decorator_usage),
        ("Comprehensive Logger", example_comprehensive_logger)
    ]
    
    log_dirs = []
    
    for name, example_func in examples:
        print(f"\n{'='*20} {name} {'='*20}")
        log_dir = example_func()
        log_dirs.append((name, log_dir))
        show_log_structure(log_dir)
    
    print(f"\n{'='*50}")
    print("ALL EXAMPLES COMPLETED!")
    print(f"{'='*50}")
    
    print(f"\nLog directories created:")
    for name, log_dir in log_dirs:
        print(f"  • {name}: {log_dir}")
    
    print(f"\nEach log directory contains:")
    print(f"  • application.log - Main application operations")
    print(f"  • system.log - System information and session data")
    print(f"  • performance.log - Performance metrics and timing")
    print(f"  • file_operations.log - All file operations")
    print(f"  • progress.log - Progress updates")
    print(f"  • external_tools.log - External tool execution (BSArch, 7z)")
    print(f"  • errors.log - Detailed error information with stack traces")
    print(f"  • user_actions.log - User interactions")
    print(f"  • configuration.log - Configuration changes")
    print(f"  • session_metadata.json - System and session information")
    print(f"  • session_summary.json - Session summary and performance data")
