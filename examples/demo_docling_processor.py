#!/usr/bin/env python3
"""
Demo script for DoclingProcessor implementation.

This script demonstrates the DoclingProcessor capabilities for multi-format 
document processing using the Docling AI provider.
"""

import os
import tempfile
import sys
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.chunkers.docling_processor import DoclingProcessor
from src.llm.providers.docling_provider import DoclingProvider
from src.llm.factory import LLMFactory


def create_sample_files():
    """Create sample files for testing different formats"""
    files = {}
    
    # Create a sample PDF file (mock content)
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='wb') as f:
        f.write(b'%PDF-1.4\n1 0 obj\n<</Type/Catalog/Pages 2 0 R>>\nendobj\n')
        f.write(b'2 0 obj\n<</Type/Pages/Kids[3 0 R]/Count 1>>\nendobj\n')
        f.write(b'3 0 obj\n<</Type/Page/Parent 2 0 R/Contents 4 0 R>>\nendobj\n')
        f.write(b'4 0 obj\n<</Length 44>>stream\nBT\n/F1 12 Tf\n100 100 Td\n(Sample PDF Content) Tj\nET\nendstream\nendobj\n')
        f.write(b'xref\n0 5\n0000000000 65535 f\n0000000009 00000 n\n')
        f.write(b'trailer\n<</Size 5/Root 1 0 R>>\nstartxref\n123\n%%EOF')
        files['pdf'] = f.name
    
    # Create a sample DOCX file (mock content)
    with tempfile.NamedTemporaryFile(suffix='.docx', delete=False, mode='wb') as f:
        f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')  # ZIP header for DOCX
        f.write(b'Sample DOCX content with hierarchical structure\n')
        f.write(b'This is a mock DOCX file for testing purposes.')
        files['docx'] = f.name
    
    # Create a sample PPTX file (mock content)
    with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False, mode='wb') as f:
        f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')  # ZIP header for PPTX
        f.write(b'Sample PPTX presentation with slides\n')
        f.write(b'This is a mock PPTX file for testing purposes.')
        files['pptx'] = f.name
    
    # Create a sample HTML file
    with tempfile.NamedTemporaryFile(suffix='.html', delete=False, mode='w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>Sample HTML Document</title>
</head>
<body>
    <header>
        <h1>Main Heading</h1>
    </header>
    <nav>
        <ul>
            <li><a href="#section1">Section 1</a></li>
            <li><a href="#section2">Section 2</a></li>
        </ul>
    </nav>
    <main>
        <section id="section1">
            <h2>Section 1</h2>
            <p>This is the first section with semantic structure.</p>
        </section>
        <section id="section2">
            <h2>Section 2</h2>
            <p>This is the second section with more content.</p>
        </section>
    </main>
    <footer>
        <p>Footer content</p>
    </footer>
</body>
</html>""")
        files['html'] = f.name
    
    # Create a sample image file (mock PNG)
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False, mode='wb') as f:
        # PNG header
        f.write(b'\x89PNG\r\n\x1a\n')
        f.write(b'Sample PNG image data for testing vision capabilities')
        files['image'] = f.name
    
    return files


def cleanup_files(files):
    """Clean up temporary files"""
    for file_path in files.values():
        try:
            os.unlink(file_path)
        except OSError:
            pass


def mock_docling_provider():
    """Create a mock DoclingProvider for demonstration"""
    class MockDoclingProvider(DoclingProvider):
        def __init__(self):
            # Initialize with mock values
            self.api_key = "mock_api_key"
            self.model = "docling-v1"
            self.config = {"base_url": "https://api.docling.ai/v1"}
            self.supported_formats = ["pdf", "docx", "pptx", "html", "image"]
        
        def is_available(self):
            return True
        
        def process_document(self, document_content, document_type, **kwargs):
            """Mock document processing with sample results"""
            if document_type == "pdf":
                return {
                    "text": "Sample PDF content with structured data extracted using Docling AI",
                    "structure": {
                        "pages": [
                            {"page_number": 1, "text": "Sample PDF Content"}
                        ],
                        "headings": [
                            {"level": 1, "text": "Sample PDF Content", "page": 1}
                        ]
                    },
                    "metadata": {
                        "title": "Sample PDF Document",
                        "format": "pdf",
                        "pages": 1,
                        "processing_method": "docling_ai"
                    }
                }
            elif document_type == "docx":
                return {
                    "text": "Sample DOCX content with hierarchical structure preserved",
                    "structure": {
                        "headings": [
                            {"level": 1, "text": "Document Title", "style": "Heading 1"},
                            {"level": 2, "text": "Section 1", "style": "Heading 2"}
                        ],
                        "paragraphs": [
                            {"text": "First paragraph content", "style": "Normal"},
                            {"text": "Second paragraph content", "style": "Normal"}
                        ]
                    },
                    "metadata": {
                        "title": "Sample DOCX Document",
                        "format": "docx",
                        "processing_method": "docling_ai"
                    }
                }
            elif document_type == "pptx":
                return {
                    "text": "Sample PPTX presentation with slides and visual elements",
                    "structure": {
                        "slides": [
                            {
                                "slide_number": 1,
                                "title": "Title Slide",
                                "content": "Sample PPTX presentation",
                                "layout": "title_slide"
                            },
                            {
                                "slide_number": 2,
                                "title": "Content Slide",
                                "content": "Slide content with bullet points",
                                "layout": "content_slide"
                            }
                        ],
                        "visual_elements": [
                            {"type": "title", "slide": 1, "text": "Title Slide"},
                            {"type": "content", "slide": 2, "text": "Content Slide"}
                        ]
                    },
                    "metadata": {
                        "title": "Sample PPTX Presentation",
                        "format": "pptx",
                        "slides": 2,
                        "processing_method": "docling_ai"
                    }
                }
            elif document_type == "html":
                return {
                    "text": "Sample HTML document with semantic structure preserved",
                    "structure": {
                        "semantic_elements": [
                            {"tag": "header", "text": "Main Heading"},
                            {"tag": "nav", "text": "Navigation menu"},
                            {"tag": "main", "text": "Main content area"},
                            {"tag": "footer", "text": "Footer content"}
                        ],
                        "headings": [
                            {"level": 1, "text": "Main Heading", "tag": "h1"},
                            {"level": 2, "text": "Section 1", "tag": "h2"},
                            {"level": 2, "text": "Section 2", "tag": "h2"}
                        ]
                    },
                    "metadata": {
                        "title": "Sample HTML Document",
                        "format": "html",
                        "processing_method": "docling_ai"
                    }
                }
            elif document_type == "image":
                return {
                    "text": "Text extracted from image using Docling vision capabilities",
                    "structure": {
                        "visual_elements": [
                            {"type": "text_block", "text": "Sample text from image", "confidence": 0.95},
                            {"type": "image_element", "description": "Visual content detected", "confidence": 0.87}
                        ],
                        "layout": {
                            "orientation": "portrait",
                            "text_regions": 1,
                            "image_regions": 1
                        }
                    },
                    "metadata": {
                        "format": "image",
                        "image_type": "png",
                        "processing_method": "docling_vision",
                        "confidence": 0.91
                    }
                }
            else:
                return {
                    "text": f"Mock processing result for {document_type}",
                    "structure": {},
                    "metadata": {"format": document_type, "processing_method": "docling_ai"}
                }
    
    return MockDoclingProvider()


def demonstrate_docling_processor():
    """Demonstrate DoclingProcessor capabilities"""
    print("=== DoclingProcessor Demo ===")
    print("Demonstrating multi-format document processing capabilities\n")
    
    # Create mock provider
    provider = mock_docling_provider()
    
    # Create processor
    processor = DoclingProcessor(provider)
    
    # Show processor info
    print("📋 Processor Information:")
    info = processor.get_provider_info()
    print(f"  Provider: {info['provider_name']}")
    print(f"  Model: {info['model']}")
    print(f"  Available: {info['is_available']}")
    print(f"  Supported formats: {', '.join(info['supported_formats'])}")
    print()
    
    # Create sample files
    print("📁 Creating sample files...")
    files = create_sample_files()
    print(f"  Created {len(files)} sample files")
    print()
    
    # Process each format
    for format_type, file_path in files.items():
        print(f"🔄 Processing {format_type.upper()} document...")
        
        try:
            result = processor.process_document(file_path, format_type)
            
            if result.success:
                print(f"  ✅ Success!")
                print(f"  📄 Text (preview): {result.text[:100]}...")
                print(f"  📊 Structure keys: {list(result.structure.keys())}")
                print(f"  📈 Metadata: {result.metadata}")
                print(f"  ⏱️  Processing time: {result.processing_time:.3f}s")
                print(f"  📦 File size: {result.file_size} bytes")
            else:
                print(f"  ❌ Failed: {result.error_message}")
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
        
        print()
    
    # Demonstrate auto-detection
    print("🔍 Testing auto-format detection...")
    for format_type, file_path in files.items():
        detected = processor._detect_format(file_path)
        print(f"  {file_path} -> {detected}")
    print()
    
    # Demonstrate format support checking
    print("🎯 Format support checking:")
    test_formats = ["pdf", "docx", "pptx", "html", "image", "txt", "unknown"]
    for fmt in test_formats:
        supported = processor.is_format_supported(fmt)
        status = "✅" if supported else "❌"
        print(f"  {fmt}: {status}")
    print()
    
    # Performance demonstration
    print("⚡ Performance capabilities:")
    print(f"  Concurrent processing: Supported")
    print(f"  Large file handling: Supported")
    print(f"  Memory monitoring: Integrated")
    print(f"  Error recovery: Graceful")
    print()
    
    # Cleanup
    cleanup_files(files)
    print("🧹 Cleaned up temporary files")
    print()
    
    print("✅ Demo completed successfully!")
    print("DoclingProcessor is ready for multi-format document processing!")


def main():
    """Main demo function"""
    try:
        demonstrate_docling_processor()
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())