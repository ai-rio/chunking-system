#!/usr/bin/env python3
"""
Demo script for Enhanced FileHandler functionality.
Showcases format detection, intelligent routing, and batch processing.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

from src.utils.enhanced_file_handler import EnhancedFileHandler, FileInfo
from src.utils.file_handler import FileHandler
from src.chunkers.docling_processor import DoclingProcessor, ProcessingResult


def create_test_files():
    """Create test files for demonstration"""
    temp_dir = tempfile.mkdtemp()
    
    # Create test files with different formats
    test_files = {
        'document.pdf': b'%PDF-1.4\n%EOF\n',
        'presentation.pptx': b'PK\x03\x04\x14\x00\x00\x00\x08\x00',
        'webpage.html': b'<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test Page</h1></body></html>',
        'readme.md': b'# Test Project\n\nThis is a test markdown file.\n\n## Features\n\n- Feature 1\n- Feature 2',
        'image.png': b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82',
        'document.docx': b'PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00',
        'unsupported.xyz': b'This is an unsupported format'
    }
    
    for filename, content in test_files.items():
        filepath = os.path.join(temp_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(content)
    
    return temp_dir


def demo_format_detection(enhanced_handler, test_dir):
    """Demonstrate format detection capabilities"""
    print("=== FORMAT DETECTION DEMO ===")
    
    for filename in os.listdir(test_dir):
        filepath = os.path.join(test_dir, filename)
        try:
            detected_format = enhanced_handler.detect_format(filepath)
            print(f"📄 {filename:20} → {detected_format}")
        except Exception as e:
            print(f"❌ {filename:20} → ERROR: {str(e)}")
    
    print()


def demo_file_discovery(enhanced_handler, test_dir):
    """Demonstrate supported file discovery"""
    print("=== FILE DISCOVERY DEMO ===")
    
    try:
        supported_files = enhanced_handler.find_supported_files(test_dir)
        print(f"Found {len(supported_files)} supported files:")
        
        for file_info in supported_files:
            size_kb = file_info.file_size / 1024
            print(f"  📁 {os.path.basename(file_info.file_path):20} | {file_info.format_type:10} | {size_kb:.1f}KB | {file_info.mime_type}")
    
    except Exception as e:
        print(f"❌ Error discovering files: {str(e)}")
    
    print()


def demo_intelligent_routing(enhanced_handler, test_dir):
    """Demonstrate intelligent routing to processors"""
    print("=== INTELLIGENT ROUTING DEMO ===")
    
    test_files = [
        'readme.md',
        'document.pdf',
        'presentation.pptx',
        'webpage.html',
        'image.png'
    ]
    
    for filename in test_files:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            try:
                format_type = enhanced_handler.detect_format(filepath)
                result = enhanced_handler.route_to_processor(filepath, format_type)
                
                status = "✅ SUCCESS" if result.success else "❌ FAILED"
                processor = "DoclingProcessor" if format_type != 'markdown' else "MarkdownProcessor"
                
                print(f"  {filename:20} → {processor:18} → {status}")
                
                if result.success:
                    content_preview = result.text[:50].replace('\n', ' ') + "..." if len(result.text) > 50 else result.text
                    print(f"    📝 Content: {content_preview}")
                    print(f"    ⏱️  Time: {result.processing_time:.3f}s")
                    print(f"    📊 Size: {result.file_size} bytes")
                else:
                    print(f"    ❌ Error: {result.error_message}")
                
            except Exception as e:
                print(f"  {filename:20} → ERROR: {str(e)}")
        else:
            print(f"  {filename:20} → FILE NOT FOUND")
    
    print()


def demo_batch_processing(enhanced_handler, test_dir):
    """Demonstrate batch processing of mixed formats"""
    print("=== BATCH PROCESSING DEMO ===")
    
    # Get all test files
    test_files = []
    for filename in os.listdir(test_dir):
        if not filename.endswith('.xyz'):  # Skip unsupported format
            test_files.append(os.path.join(test_dir, filename))
    
    try:
        results = enhanced_handler.process_batch(test_files)
        
        print(f"Processed {len(results)} files in batch:")
        
        success_count = sum(1 for r in results if r.success)
        failed_count = len(results) - success_count
        
        print(f"  ✅ Successful: {success_count}")
        print(f"  ❌ Failed: {failed_count}")
        
        # Show details for each result
        for result in results:
            filename = os.path.basename(result.file_path)
            status = "✅" if result.success else "❌"
            print(f"    {status} {filename:20} ({result.format_type:10}) - {result.processing_time:.3f}s")
            
    except Exception as e:
        print(f"❌ Batch processing error: {str(e)}")
    
    print()


def demo_validation_and_security(enhanced_handler, test_dir):
    """Demonstrate file validation and security features"""
    print("=== VALIDATION & SECURITY DEMO ===")
    
    test_cases = [
        ('document.pdf', 'pdf'),
        ('readme.md', 'markdown'),
        ('image.png', 'image'),
        ('document.pdf', 'docx'),  # Wrong format
        ('unsupported.xyz', 'pdf'),  # Unsupported file
    ]
    
    for filename, expected_format in test_cases:
        filepath = os.path.join(test_dir, filename)
        if os.path.exists(filepath):
            is_valid = enhanced_handler.validate_file_format(filepath, expected_format)
            status = "✅ VALID" if is_valid else "❌ INVALID"
            print(f"  {filename:20} as {expected_format:10} → {status}")
        else:
            print(f"  {filename:20} as {expected_format:10} → FILE NOT FOUND")
    
    print()


def demo_backward_compatibility(enhanced_handler, test_dir):
    """Demonstrate backward compatibility with existing functionality"""
    print("=== BACKWARD COMPATIBILITY DEMO ===")
    
    # Test that existing markdown finding still works
    try:
        supported_files = enhanced_handler.find_supported_files(test_dir)
        markdown_files = [f for f in supported_files if f.format_type == 'markdown']
        
        print(f"Found {len(markdown_files)} markdown files via enhanced handler:")
        for md_file in markdown_files:
            print(f"  📝 {os.path.basename(md_file.file_path)}")
        
        # Show that format detection maintains consistency
        print("\nFormat detection consistency:")
        formats = enhanced_handler.get_supported_formats()
        print(f"  Supported formats: {', '.join(sorted(formats))}")
        
    except Exception as e:
        print(f"❌ Backward compatibility error: {str(e)}")
    
    print()


def main():
    """Main demonstration function"""
    print("🚀 Enhanced FileHandler Demo")
    print("=" * 50)
    
    # Create mock dependencies
    mock_file_handler = Mock(spec=FileHandler)
    mock_docling_processor = Mock(spec=DoclingProcessor)
    
    # Configure mock responses
    mock_file_handler.find_markdown_files.return_value = []
    
    def mock_process_document(file_path, format_type):
        """Mock processor that returns realistic results"""
        file_size = os.path.getsize(file_path)
        
        if format_type == 'pdf':
            return ProcessingResult(
                format_type=format_type,
                file_path=file_path,
                success=True,
                text="This is extracted PDF content with structured data...",
                structure={"pages": 1, "sections": ["Introduction", "Content"]},
                metadata={"author": "Test Author", "title": "Test Document"},
                processing_time=0.25,
                file_size=file_size
            )
        else:
            return ProcessingResult(
                format_type=format_type,
                file_path=file_path,
                success=True,
                text=f"Processed {format_type} content...",
                structure={"type": format_type},
                metadata={"processed": True},
                processing_time=0.15,
                file_size=file_size
            )
    
    mock_docling_processor.process_document.side_effect = mock_process_document
    
    # Create enhanced handler
    enhanced_handler = EnhancedFileHandler(
        file_handler=mock_file_handler,
        docling_processor=mock_docling_processor
    )
    
    # Create test environment
    test_dir = create_test_files()
    
    try:
        # Run demonstrations
        demo_format_detection(enhanced_handler, test_dir)
        demo_file_discovery(enhanced_handler, test_dir)
        demo_intelligent_routing(enhanced_handler, test_dir)
        demo_batch_processing(enhanced_handler, test_dir)
        demo_validation_and_security(enhanced_handler, test_dir)
        demo_backward_compatibility(enhanced_handler, test_dir)
        
        print("🎉 Demo completed successfully!")
        print("✅ All Enhanced FileHandler features demonstrated")
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)


if __name__ == "__main__":
    main()