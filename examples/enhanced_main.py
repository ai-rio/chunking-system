#!/usr/bin/env python3
"""
Enhanced main application for document chunking system with multi-format support.
Integrates EnhancedFileHandler for PDF, DOCX, PPTX, HTML, image, and Markdown processing.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse
from tqdm import tqdm
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env if python-dotenv not available
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#') and '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Remove quotes if present
                    value = value.strip('"\'')
                    os.environ[key] = value

# Add src to path for module imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import logging utilities
from src.utils.logger import setup_logging, get_chunking_logger, ChunkingLogger
from src.utils.validators import (
    validate_file_path, validate_directory_path, validate_chunk_size, 
    validate_chunk_overlap, validate_output_format
)
from src.utils.path_utils import get_markdown_manager, get_advanced_quality_enhancement_manager

# Setup logging
app_logger = setup_logging(level="INFO")
chunking_logger = get_chunking_logger()
path_manager = get_markdown_manager()

# Import enhanced components
from src.utils.enhanced_file_handler import EnhancedFileHandler, FileInfo
from src.utils.file_handler import FileHandler
from src.chunkers.docling_processor import DoclingProcessor
from src.llm.providers.docling_provider import DoclingProvider
from src.utils.metadata_enricher import MetadataEnricher
from src.chunkers.evaluators import ChunkQualityEvaluator, EnhancedChunkQualityEvaluator
from src.config.settings import config
from src.exceptions import ChunkingError, FileHandlingError, ValidationError


def progress_callback(current: int, total: int, filename: str):
    """Callback for progress tracking during file processing."""
    chunking_logger.log_batch_progress(current, total, os.path.basename(filename))


def setup_enhanced_file_handler() -> EnhancedFileHandler:
    """
    Initialize and configure the enhanced file handler.
    
    Returns:
        EnhancedFileHandler: Configured handler instance
    """
    try:
        # Initialize base components
        file_handler = FileHandler()
        
        # Initialize DoclingProvider (you may need to configure this based on your setup)
        docling_provider = DoclingProvider(
            # Configure provider parameters as needed
            api_key=os.getenv('DOCLING_API_KEY'),
            model="docling-v1",
            base_url=os.getenv('DOCLING_BASE_URL')
        )
        
        # Initialize DoclingProcessor
        docling_processor = DoclingProcessor(docling_provider=docling_provider)
        
        # Create enhanced file handler
        enhanced_handler = EnhancedFileHandler(
            file_handler=file_handler,
            docling_processor=docling_processor
        )
        
        return enhanced_handler
        
    except Exception as e:
        app_logger.error("Failed to initialize enhanced file handler", error=str(e))
        raise


def process_single_file(enhanced_handler: EnhancedFileHandler, input_file: str, args) -> Dict[str, Any]:
    """
    Process a single file with format detection and routing.
    
    Args:
        enhanced_handler: Enhanced file handler instance
        input_file: Path to input file
        args: Command line arguments
        
    Returns:
        Dict containing processing results
    """
    chunking_logger.start_operation("single_file_processing", file_path=input_file)
    
    try:
        # Detect format
        format_type = enhanced_handler.detect_format(input_file)
        app_logger.info("Format detected", file_path=input_file, format=format_type)
        
        # Validate format
        if not enhanced_handler.validate_file_format(input_file, format_type):
            raise ValidationError(f"File validation failed for {input_file} as {format_type}")
        
        # Route to appropriate processor
        result = enhanced_handler.route_to_processor(input_file, format_type)
        
        if not result.success:
            raise FileHandlingError(f"Processing failed: {result.error_message}")
        
        # Convert to chunks format for downstream processing
        chunks = [{
            'content': result.text,
            'metadata': {
                **result.metadata,
                'source': input_file,
                'format_type': format_type,
                'file_size': result.file_size,
                'processing_time': result.processing_time
            }
        }]
        
        chunking_logger.end_operation("single_file_processing", success=True)
        
        return {
            'success': True,
            'format_type': format_type,
            'chunks': chunks,
            'processing_time': result.processing_time,
            'file_size': result.file_size
        }
        
    except Exception as e:
        chunking_logger.log_error(e, "single_file_processing")
        chunking_logger.end_operation("single_file_processing", success=False)
        
        return {
            'success': False,
            'error': str(e),
            'format_type': 'unknown',
            'chunks': [],
            'processing_time': 0,
            'file_size': 0
        }


def process_directory(enhanced_handler: EnhancedFileHandler, input_dir: str, args) -> Dict[str, Any]:
    """
    Process all supported files in a directory.
    
    Args:
        enhanced_handler: Enhanced file handler instance
        input_dir: Path to input directory
        args: Command line arguments
        
    Returns:
        Dict containing processing results
    """
    chunking_logger.start_operation("directory_processing", directory=input_dir)
    
    try:
        # Find all supported files
        supported_files = enhanced_handler.find_supported_files(input_dir)
        
        if not supported_files:
            app_logger.warning("No supported files found in directory", directory=input_dir)
            return {
                'success': True,
                'files_processed': 0,
                'total_chunks': 0,
                'formats_found': [],
                'processing_results': []
            }
        
        app_logger.info("Found supported files", count=len(supported_files), directory=input_dir)
        
        # Process files in batch
        file_paths = [f.file_path for f in supported_files]
        results = enhanced_handler.process_batch(file_paths)
        
        # Aggregate results
        successful_files = sum(1 for r in results if r.success)
        failed_files = len(results) - successful_files
        formats_found = list(set(r.format_type for r in results))
        
        all_chunks = []
        processing_results = []
        
        for result in results:
            if result.success:
                chunks = [{
                    'content': result.text,
                    'metadata': {
                        **result.metadata,
                        'source': result.file_path,
                        'format_type': result.format_type,
                        'file_size': result.file_size,
                        'processing_time': result.processing_time
                    }
                }]
                all_chunks.extend(chunks)
            
            processing_results.append({
                'file_path': result.file_path,
                'format_type': result.format_type,
                'success': result.success,
                'error_message': result.error_message if not result.success else None,
                'processing_time': result.processing_time,
                'file_size': result.file_size
            })
        
        chunking_logger.end_operation("directory_processing", success=True)
        
        return {
            'success': True,
            'files_processed': successful_files,
            'files_failed': failed_files,
            'total_chunks': len(all_chunks),
            'formats_found': formats_found,
            'chunks': all_chunks,
            'processing_results': processing_results
        }
        
    except Exception as e:
        chunking_logger.log_error(e, "directory_processing")
        chunking_logger.end_operation("directory_processing", success=False)
        
        return {
            'success': False,
            'error': str(e),
            'files_processed': 0,
            'total_chunks': 0,
            'formats_found': [],
            'chunks': []
        }


def main():
    """Enhanced main function with multi-format support."""
    chunking_logger.start_operation("enhanced_main_application")
    app_logger.info("Starting enhanced document chunking system with multi-format support")
    
    parser = argparse.ArgumentParser(description="Enhanced Document Chunking System with Multi-Format Support")
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        '--input-file',
        help="Path to a single document file (PDF, DOCX, PPTX, HTML, image, or Markdown)"
    )
    input_group.add_argument(
        '--input-dir',
        help="Directory containing documents to process (processes all supported formats)"
    )
    
    # Output options
    parser.add_argument(
        '--output-dir',
        default=config.OUTPUT_DIR,
        help="Output directory for generated chunks and reports"
    )
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'pickle'],
        default='json',
        help="Output format for the generated chunks"
    )
    
    # Processing options
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=config.DEFAULT_CHUNK_SIZE,
        help="Maximum chunk size in tokens (for chunking after processing)"
    )
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=config.DEFAULT_CHUNK_OVERLAP,
        help="Number of tokens to overlap between chunks"
    )
    
    # Enhanced options
    parser.add_argument(
        '--supported-formats',
        action='store_true',
        help="List all supported file formats and exit"
    )
    parser.add_argument(
        '--detect-format',
        help="Detect and display format of a specific file"
    )
    parser.add_argument(
        '--validate-file',
        help="Validate a specific file and display results"
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help="Number of files to process in parallel (for directory processing)"
    )
    
    # Quality and enhancement options
    parser.add_argument(
        '--auto-enhance',
        action='store_true',
        default=False,
        help="Automatically enhance chunks if quality is below threshold"
    )
    parser.add_argument(
        '--jina-api-key',
        help="Jina AI API key for enhanced quality evaluation"
    )
    parser.add_argument(
        '--create-project-folder',
        action='store_true',
        default=True,
        help="Create a timestamped project folder for each run"
    )
    
    args = parser.parse_args()
    
    # Handle utility commands
    if args.supported_formats:
        try:
            enhanced_handler = setup_enhanced_file_handler()
            formats = enhanced_handler.get_supported_formats()
            print("Supported file formats:")
            for fmt in sorted(formats):
                print(f"  - {fmt}")
            return
        except Exception as e:
            app_logger.error("Failed to list supported formats", error=str(e))
            return
    
    if args.detect_format:
        try:
            enhanced_handler = setup_enhanced_file_handler()
            format_type = enhanced_handler.detect_format(args.detect_format)
            print(f"File: {args.detect_format}")
            print(f"Detected format: {format_type}")
            return
        except Exception as e:
            app_logger.error("Failed to detect format", error=str(e))
            return
    
    if args.validate_file:
        try:
            enhanced_handler = setup_enhanced_file_handler()
            format_type = enhanced_handler.detect_format(args.validate_file)
            is_valid = enhanced_handler.validate_file_format(args.validate_file, format_type)
            print(f"File: {args.validate_file}")
            print(f"Format: {format_type}")
            print(f"Valid: {'Yes' if is_valid else 'No'}")
            return
        except Exception as e:
            app_logger.error("Failed to validate file", error=str(e))
            return
    
    # Initialize enhanced file handler
    try:
        enhanced_handler = setup_enhanced_file_handler()
        app_logger.info("Enhanced file handler initialized successfully")
    except Exception as e:
        app_logger.error("Failed to initialize enhanced file handler", error=str(e))
        chunking_logger.end_operation("enhanced_main_application", success=False, error="Handler initialization failed")
        return
    
    # Process input
    processing_results = None
    
    if args.input_file:
        # Single file processing
        try:
            # Validate input file
            input_file_path = validate_file_path(args.input_file, must_exist=True)
            app_logger.info("Processing single file", file_path=str(input_file_path))
            
            processing_results = process_single_file(enhanced_handler, str(input_file_path), args)
            
        except (ValidationError, FileHandlingError) as e:
            app_logger.error("Input validation failed", error=str(e))
            chunking_logger.end_operation("enhanced_main_application", success=False, error="Input validation failed")
            return
        except Exception as e:
            app_logger.error("Unexpected error during single file processing", error=str(e))
            chunking_logger.end_operation("enhanced_main_application", success=False, error="Processing failed")
            return
    
    elif args.input_dir:
        # Directory processing
        try:
            # Validate input directory
            input_dir_path = validate_directory_path(args.input_dir, must_exist=True)
            app_logger.info("Processing directory", directory=str(input_dir_path))
            
            processing_results = process_directory(enhanced_handler, str(input_dir_path), args)
            
        except (ValidationError, FileHandlingError) as e:
            app_logger.error("Input validation failed", error=str(e))
            chunking_logger.end_operation("enhanced_main_application", success=False, error="Input validation failed")
            return
        except Exception as e:
            app_logger.error("Unexpected error during directory processing", error=str(e))
            chunking_logger.end_operation("enhanced_main_application", success=False, error="Processing failed")
            return
    
    # Handle processing results
    if not processing_results or not processing_results['success']:
        error_msg = processing_results.get('error', 'Unknown error') if processing_results else 'No processing results'
        app_logger.error("Processing failed", error=error_msg)
        chunking_logger.end_operation("enhanced_main_application", success=False, error=error_msg)
        return
    
    # Save results
    try:
        # Setup output directories
        if args.input_file:
            base_name = Path(args.input_file).stem
        else:
            base_name = Path(args.input_dir).name
        
        output_dir = Path(args.output_dir)
        if args.create_project_folder:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = output_dir / f"{base_name}_{timestamp}"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        chunks_dir = output_dir / "chunks"
        reports_dir = output_dir / "reports"
        chunks_dir.mkdir(exist_ok=True)
        reports_dir.mkdir(exist_ok=True)
        
        # Save chunks
        chunks = processing_results.get('chunks', [])
        if chunks:
            if args.format == 'json':
                output_path = chunks_dir / f"{base_name}_chunks.json"
            elif args.format == 'csv':
                output_path = chunks_dir / f"{base_name}_chunks.csv"
            else:  # pickle
                output_path = chunks_dir / f"{base_name}_chunks.pickle"
            
            # Convert to Document objects for FileHandler
            from langchain_core.documents import Document
            documents = [Document(page_content=chunk['content'], metadata=chunk['metadata']) for chunk in chunks]
            
            FileHandler.save_chunks(documents, str(output_path), args.format)
            app_logger.info("Chunks saved successfully", output_path=str(output_path))
        
        # Save processing report
        report_path = reports_dir / f"{base_name}_processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(processing_results, f, indent=2, default=str)
        
        app_logger.info("Processing completed successfully",
                       chunks_generated=len(chunks),
                       output_directory=str(output_dir),
                       report_path=str(report_path))
        
        # Summary
        if args.input_file:
            print(f"✅ Successfully processed file: {args.input_file}")
            print(f"📄 Format: {processing_results.get('format_type', 'unknown')}")
            print(f"📊 Chunks generated: {len(chunks)}")
        else:
            print(f"✅ Successfully processed directory: {args.input_dir}")
            print(f"📁 Files processed: {processing_results.get('files_processed', 0)}")
            print(f"📄 Formats found: {', '.join(processing_results.get('formats_found', []))}")
            print(f"📊 Total chunks: {len(chunks)}")
        
        print(f"💾 Output saved to: {output_dir}")
        
        chunking_logger.end_operation("enhanced_main_application", success=True, chunks_generated=len(chunks))
        
    except Exception as e:
        app_logger.error("Failed to save results", error=str(e))
        chunking_logger.end_operation("enhanced_main_application", success=False, error="Result saving failed")
        return


if __name__ == "__main__":
    main()