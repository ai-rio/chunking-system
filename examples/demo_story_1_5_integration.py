#!/usr/bin/env python3
"""
Story 1.5 End-to-End Integration Demo
Demonstrates complete multi-format processing pipeline with production readiness.
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any
import tempfile
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.orchestration.production_pipeline import ProductionPipeline, PipelineConfig, create_production_pipeline
from src.utils.logger import setup_logging


def create_sample_documents(temp_dir: Path) -> List[str]:
    """Create sample documents for demonstration."""
    files = []
    
    # Markdown document
    md_content = """# Story 1.5 Integration Demo
    
This document demonstrates the complete multi-format processing pipeline.

## Key Features
- **Multi-format support**: PDF, DOCX, PPTX, HTML, images, and Markdown
- **Quality evaluation**: Format-specific quality metrics
- **Performance monitoring**: Production-ready performance tracking
- **Error handling**: Comprehensive error recovery
- **Batch processing**: Concurrent document processing

## Code Example
```python
def process_document(file_path):
    processor = DoclingProcessor(provider)
    chunks = processor.process_document(file_path)
    return chunks
```

## Benefits
1. **Unified processing**: Single interface for all formats
2. **Production ready**: Monitoring and error handling
3. **Scalable**: Concurrent processing support
4. **Quality assured**: Multi-format quality evaluation
"""
    
    md_file = temp_dir / "demo_document.md"
    md_file.write_text(md_content)
    files.append(str(md_file))
    
    # HTML document
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Story 1.5 HTML Demo</title>
</head>
<body>
    <h1>HTML Document Processing Demo</h1>
    <p>This HTML document will be processed using the Docling multi-format pipeline.</p>
    
    <h2>Processing Steps</h2>
    <ol>
        <li>Format detection and routing</li>
        <li>Content extraction and chunking</li>
        <li>Quality evaluation with HTML-specific metrics</li>
        <li>Metadata enrichment</li>
        <li>Performance monitoring</li>
    </ol>
    
    <h2>Expected Results</h2>
    <p>The pipeline should successfully extract content, maintain structure, 
    and provide quality metrics specific to HTML documents.</p>
</body>
</html>"""
    
    html_file = temp_dir / "demo_document.html"
    html_file.write_text(html_content)
    files.append(str(html_file))
    
    # Plain text document (will be processed as unknown format)
    text_content = """Story 1.5 Integration - Plain Text Demo

This plain text document demonstrates fallback processing for unknown formats.

The system should detect this as an unknown format and process it using 
the fallback markdown processor while maintaining backward compatibility.

Key integration points:
- Format detection and routing
- Fallback processing for unknown formats
- Quality evaluation with adaptive metrics
- Performance monitoring across all formats
- Error handling and recovery mechanisms

This demonstrates the robustness of the integrated system."""
    
    text_file = temp_dir / "demo_document.txt"
    text_file.write_text(text_content)
    files.append(str(text_file))
    
    return files


def demonstrate_single_document_processing(pipeline: ProductionPipeline, file_path: str):
    """Demonstrate processing a single document."""
    print(f"\n🔄 Processing single document: {Path(file_path).name}")
    
    # Process the document
    result = pipeline.process_single_document(file_path)
    
    if result.success:
        print(f"✅ Successfully processed {result.format_type} document")
        print(f"   - Chunks generated: {len(result.chunks)}")
        print(f"   - Processing time: {result.processing_time:.2f}s")
        print(f"   - Quality score: {result.quality_metrics.get('overall_score', 'N/A')}")
        
        # Show first chunk preview
        if result.chunks:
            first_chunk = result.chunks[0]
            preview = first_chunk.page_content[:200] + "..." if len(first_chunk.page_content) > 200 else first_chunk.page_content
            print(f"   - First chunk preview: {preview}")
    else:
        print(f"❌ Failed to process document: {result.error_message}")
    
    return result


def demonstrate_batch_processing(pipeline: ProductionPipeline, file_paths: List[str]):
    """Demonstrate batch processing of multiple documents."""
    print(f"\n🔄 Processing batch of {len(file_paths)} documents")
    
    # Process all documents in batch
    results = pipeline.process_batch(file_paths)
    
    # Show results summary
    successful = sum(1 for r in results if r.success)
    failed = len(results) - successful
    
    print(f"✅ Batch processing completed:")
    print(f"   - Total files: {len(results)}")
    print(f"   - Successful: {successful}")
    print(f"   - Failed: {failed}")
    print(f"   - Success rate: {successful/len(results)*100:.1f}%")
    
    # Show per-file results
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"   {status} {Path(result.file_path).name} ({result.format_type}) - {result.processing_time:.2f}s")
    
    return results


def demonstrate_performance_monitoring(pipeline: ProductionPipeline):
    """Demonstrate performance monitoring capabilities."""
    print(f"\n📊 Performance Monitoring")
    
    # Get processing statistics
    stats = pipeline.get_processing_stats()
    print(f"Processing Statistics:")
    print(f"   - Total files processed: {stats['total_files']}")
    print(f"   - Success rate: {stats['success_rate']:.1f}%")
    print(f"   - Average processing time: {stats['average_processing_time']:.2f}s")
    print(f"   - Total chunks generated: {stats['total_chunks']}")
    print(f"   - Average chunks per file: {stats['average_chunks_per_file']:.1f}")
    
    # Show format distribution
    if stats['format_distribution']:
        print(f"Format Distribution:")
        for format_type, count in stats['format_distribution'].items():
            print(f"   - {format_type}: {count} files")
    
    # Get system health
    health = pipeline.get_system_health()
    print(f"System Health:")
    print(f"   - Status: {health.get('status', 'unknown')}")
    print(f"   - CPU usage: {health.get('cpu_usage', 0):.1f}%")
    print(f"   - Memory usage: {health.get('memory_usage', 0):.1f}%")
    print(f"   - Disk usage: {health.get('disk_usage', 0):.1f}%")


def demonstrate_production_readiness(pipeline: ProductionPipeline):
    """Demonstrate production readiness validation."""
    print(f"\n🚀 Production Readiness Validation")
    
    readiness = pipeline.validate_production_readiness()
    
    print(f"Production Readiness: {'✅ READY' if readiness['ready_for_production'] else '❌ NOT READY'}")
    print(f"Readiness Score: {readiness['readiness_score']:.1f}%")
    
    print(f"Component Checks:")
    for check, status in readiness['checks'].items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {check.replace('_', ' ').title()}")
    
    if readiness['recommendations']:
        print(f"Recommendations:")
        for rec in readiness['recommendations']:
            print(f"   - {rec}")


def demonstrate_comprehensive_reporting(pipeline: ProductionPipeline, results: List, output_dir: Path):
    """Demonstrate comprehensive reporting capabilities."""
    print(f"\n📋 Comprehensive Reporting")
    
    # Generate comprehensive report
    report_path = output_dir / "story_1_5_integration_report.md"
    report_content = pipeline.generate_comprehensive_report(results, str(report_path))
    
    print(f"✅ Comprehensive report generated: {report_path}")
    
    # Show report summary
    lines = report_content.split('\n')
    summary_lines = [line for line in lines if line.startswith('- **') and ('Files' in line or 'Successful' in line or 'Failed' in line)]
    
    print(f"Report Summary:")
    for line in summary_lines[:5]:  # Show first 5 summary lines
        print(f"   {line}")
    
    return report_content


def demonstrate_error_handling(pipeline: ProductionPipeline):
    """Demonstrate error handling and recovery."""
    print(f"\n🛠️ Error Handling Demo")
    
    # Try to process a non-existent file
    fake_file = "/nonexistent/fake_document.pdf"
    result = pipeline.process_single_document(fake_file)
    
    if not result.success:
        print(f"✅ Error handling working correctly:")
        print(f"   - Error detected: {result.error_message}")
        print(f"   - Processing time recorded: {result.processing_time:.2f}s")
        print(f"   - System continued operation")
    else:
        print(f"❌ Error handling may not be working correctly")


def main():
    """Main demonstration function."""
    print("🎯 Story 1.5 End-to-End Integration Demo")
    print("=" * 60)
    
    # Setup logging
    logger = setup_logging(level="INFO")
    
    # Create temporary directory for demo files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample documents
        print("📁 Creating sample documents...")
        sample_files = create_sample_documents(temp_path)
        print(f"   Created {len(sample_files)} sample documents")
        
        # Create production pipeline
        print("⚙️ Initializing production pipeline...")
        config = PipelineConfig(
            max_concurrent_files=2,
            performance_monitoring_enabled=True,
            quality_evaluation_enabled=True,
            error_recovery_enabled=True,
            output_detailed_reports=True
        )
        
        pipeline = create_production_pipeline(config)
        print("   ✅ Production pipeline initialized")
        
        # Demonstrate production readiness
        demonstrate_production_readiness(pipeline)
        
        # Demonstrate single document processing
        demonstrate_single_document_processing(pipeline, sample_files[0])
        
        # Demonstrate batch processing
        batch_results = demonstrate_batch_processing(pipeline, sample_files)
        
        # Demonstrate performance monitoring
        demonstrate_performance_monitoring(pipeline)
        
        # Demonstrate error handling
        demonstrate_error_handling(pipeline)
        
        # Demonstrate comprehensive reporting
        demonstrate_comprehensive_reporting(pipeline, batch_results, temp_path)
        
        print("\n🎉 Story 1.5 Integration Demo Completed Successfully!")
        print("=" * 60)
        
        # Show final statistics
        final_stats = pipeline.get_processing_stats()
        print(f"Final Processing Statistics:")
        print(f"   - Total documents processed: {final_stats['total_files']}")
        print(f"   - Success rate: {final_stats['success_rate']:.1f}%")
        print(f"   - Total chunks generated: {final_stats['total_chunks']}")
        print(f"   - Average processing time: {final_stats['average_processing_time']:.2f}s per document")
        
        # Production readiness summary
        readiness = pipeline.validate_production_readiness()
        readiness_status = "✅ PRODUCTION READY" if readiness['ready_for_production'] else "⚠️ NEEDS ATTENTION"
        print(f"   - Production readiness: {readiness_status} ({readiness['readiness_score']:.1f}%)")


if __name__ == "__main__":
    main()