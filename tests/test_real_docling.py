#!/usr/bin/env python3
"""
Test script using the actual Docling library when available.
This demonstrates the complete integration with the real Docling DocumentConverter.
"""

import os
import tempfile
from pathlib import Path

def test_actual_docling_integration():
    """Test with actual Docling library if available."""
    print("🔍 Testing Actual Docling Integration")
    print("=" * 50)
    
    try:
        # Test if docling is available
        from docling.document_converter import DocumentConverter
        from docling.datamodel.base_models import InputFormat
        from docling.chunking import HybridChunker
        
        print("✅ Docling library is available!")
        
        # Initialize DocumentConverter
        print("\n1. Initializing DocumentConverter...")
        converter = DocumentConverter(
            allowed_formats=[
                InputFormat.PDF,
                InputFormat.DOCX,
                InputFormat.PPTX,
                InputFormat.HTML,
                InputFormat.IMAGE,
            ]
        )
        
        # Initialize HybridChunker
        print("2. Initializing HybridChunker...")
        chunker = HybridChunker(tokenizer="sentence-transformers/all-MiniLM-L6-v2")
        
        print("✅ Real Docling components initialized successfully!")
        
        # Test with a simple HTML content
        print("\n3. Testing with HTML content...")
        html_content = """
        <!DOCTYPE html>
        <html>
        <head><title>Test Document</title></head>
        <body>
            <h1>Test HTML Document</h1>
            <p>This is a test document to verify Docling integration.</p>
            <h2>Section 1</h2>
            <p>This section contains important information.</p>
            <h2>Section 2</h2>
            <p>This section has additional details.</p>
        </body>
        </html>
        """
        
        # Create temporary HTML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_file = f.name
        
        try:
            # Convert document
            print("   Converting HTML document...")
            conversion_result = converter.convert(html_file)
            
            if conversion_result.status.success:
                print("   ✅ Document conversion successful!")
                
                # Get the DoclingDocument
                docling_doc = conversion_result.document
                
                # Export to different formats
                print("\n4. Testing export formats...")
                
                # Export to Markdown
                markdown_content = docling_doc.export_to_markdown()
                print(f"   ✅ Markdown export: {len(markdown_content)} characters")
                
                # Export to JSON
                json_content = docling_doc.export_to_json()
                print(f"   ✅ JSON export: {len(json_content)} characters")
                
                # Test chunking
                print("\n5. Testing document chunking...")
                chunks = list(chunker.chunk(docling_doc))
                print(f"   ✅ Generated {len(chunks)} chunks")
                
                for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
                    print(f"      Chunk {i+1}: {chunk.text[:80]}...")
                
                print("\n✅ All tests passed! Docling integration is working correctly.")
                return True
                
            else:
                print(f"   ❌ Document conversion failed: {conversion_result.status.error_message}")
                return False
                
        finally:
            # Clean up
            os.unlink(html_file)
            
    except ImportError as e:
        print(f"❌ Docling library not available: {e}")
        print("   Please install docling: pip install docling")
        return False
    except Exception as e:
        print(f"❌ Error testing Docling integration: {e}")
        return False


def test_updated_docling_processor():
    """Test the updated DoclingProcessor class."""
    print("\n🔧 Testing Updated DoclingProcessor")
    print("=" * 50)
    
    try:
        # Import our updated DoclingProcessor
        from src.chunkers.docling_processor import DoclingProcessor
        
        print("✅ DoclingProcessor imported successfully!")
        
        # Initialize processor
        print("\n1. Initializing DoclingProcessor...")
        processor = DoclingProcessor()
        
        # Test processor info
        print("2. Getting processor info...")
        info = processor.get_processor_info()
        print(f"   ✅ Processor: {info['processor_name']}")
        print(f"   ✅ Library: {info['library']}")
        print(f"   ✅ Supported formats: {', '.join(info['supported_formats'])}")
        
        # Test format support
        print("\n3. Testing format support...")
        formats = processor.get_supported_formats()
        assert "pdf" in formats
        assert "docx" in formats
        assert "html" in formats
        print(f"   ✅ Supports {len(formats)} formats")
        
        print("\n✅ DoclingProcessor tests passed!")
        return True
        
    except ImportError as e:
        print(f"❌ DoclingProcessor import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing DoclingProcessor: {e}")
        return False


def test_production_pipeline():
    """Test the updated production pipeline."""
    print("\n🏭 Testing Production Pipeline")
    print("=" * 50)
    
    try:
        from src.orchestration.production_pipeline import ProductionPipeline, PipelineConfig
        
        print("✅ Production pipeline imported successfully!")
        
        # Initialize pipeline
        print("\n1. Initializing production pipeline...")
        config = PipelineConfig(
            max_concurrent_files=2,
            performance_monitoring_enabled=True,
            quality_evaluation_enabled=True
        )
        
        pipeline = ProductionPipeline(config)
        print("   ✅ Pipeline initialized")
        
        # Test production readiness
        print("\n2. Checking production readiness...")
        readiness = pipeline.validate_production_readiness()
        
        print(f"   📊 Readiness score: {readiness['readiness_score']:.1f}%")
        print("   🔍 Checks:")
        for check, status in readiness['checks'].items():
            status_icon = "✅" if status else "❌"
            print(f"      {status_icon} {check}: {'PASS' if status else 'FAIL'}")
        
        if readiness['recommendations']:
            print("   💡 Recommendations:")
            for rec in readiness['recommendations']:
                print(f"      • {rec}")
        
        success = readiness['readiness_score'] >= 80
        print(f"\n{'✅' if success else '❌'} Production readiness: {'PASS' if success else 'FAIL'}")
        
        return success
        
    except ImportError as e:
        print(f"❌ Production pipeline import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing production pipeline: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Comprehensive Docling Integration Test")
    print("=" * 60)
    
    results = []
    
    # Test 1: Actual Docling library
    results.append(test_actual_docling_integration())
    
    # Test 2: Updated DoclingProcessor
    results.append(test_updated_docling_processor())
    
    # Test 3: Production pipeline
    results.append(test_production_pipeline())
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    test_names = [
        "Actual Docling Integration",
        "Updated DoclingProcessor", 
        "Production Pipeline"
    ]
    
    passed = sum(results)
    total = len(results)
    
    for i, (test_name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test_name}: {status}")
    
    print(f"\nOVERALL: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! The Docling integration is complete and working.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)