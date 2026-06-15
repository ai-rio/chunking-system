#!/usr/bin/env python3
"""
Demonstration of MultiFormatQualityEvaluator for Story 1.4
Shows enhanced quality evaluation across multiple document formats
"""

import os
from typing import List
from langchain_core.documents import Document
from src.chunkers.evaluators import ChunkQualityEvaluator
from src.chunkers.multi_format_quality_evaluator import MultiFormatQualityEvaluator


def create_sample_chunks() -> dict:
    """Create sample chunks for different document formats."""
    
    # PDF chunks with structured content
    pdf_chunks = [
        Document(
            page_content="Executive Summary\n\nThis document presents the quarterly financial results for Q3 2024. Key highlights include 15% revenue growth and improved operational efficiency.",
            metadata={
                "source": "quarterly_report.pdf",
                "page": 1,
                "format_type": "pdf",
                "has_images": False,
                "has_tables": True,
                "structure_preserved": True
            }
        ),
        Document(
            page_content="Financial Performance\n\nRevenue: $2.5M (+15% YoY)\nOperating Expenses: $1.8M (-5% YoY)\nNet Income: $0.7M (+40% YoY)",
            metadata={
                "source": "quarterly_report.pdf",
                "page": 2,
                "format_type": "pdf",
                "has_images": True,
                "has_tables": True,
                "structure_preserved": True
            }
        )
    ]
    
    # DOCX chunks with heading structure
    docx_chunks = [
        Document(
            page_content="Project Proposal: AI-Powered Document Processing\n\nOverview of our proposed solution for automated document analysis and processing.",
            metadata={
                "source": "project_proposal.docx",
                "format_type": "docx",
                "has_images": False,
                "has_tables": False,
                "structure_preserved": True,
                "heading_level": 1
            }
        ),
        Document(
            page_content="Technical Architecture\n\nThe system will use advanced NLP techniques including transformer models and vector embeddings for document understanding.",
            metadata={
                "source": "project_proposal.docx",
                "format_type": "docx",
                "has_images": True,
                "has_tables": False,
                "structure_preserved": True,
                "heading_level": 2
            }
        )
    ]
    
    # Image chunks from OCR processing
    image_chunks = [
        Document(
            page_content="SALES PERFORMANCE CHART\n\nQ1 2024: $1.2M\nQ2 2024: $1.5M\nQ3 2024: $1.8M\nQ4 2024: $2.1M (projected)",
            metadata={
                "source": "sales_chart.png",
                "format_type": "image",
                "ocr_confidence": 0.92,
                "image_type": "chart",
                "has_text": True,
                "structure_preserved": True
            }
        ),
        Document(
            page_content="Company Logo\nANNUAL REPORT 2024\nBuilding Tomorrow Today",
            metadata={
                "source": "cover_page.png",
                "format_type": "image",
                "ocr_confidence": 0.88,
                "image_type": "logo",
                "has_text": True,
                "structure_preserved": False
            }
        )
    ]
    
    # HTML chunks with semantic structure
    html_chunks = [
        Document(
            page_content="<h1>Web Development Best Practices</h1>\n<p>This guide covers essential practices for modern web development including responsive design and accessibility.</p>",
            metadata={
                "source": "web_guide.html",
                "format_type": "html",
                "has_images": False,
                "has_tables": False,
                "structure_preserved": True
            }
        ),
        Document(
            page_content="<h2>Performance Optimization</h2>\n<ul><li>Minimize HTTP requests</li><li>Optimize images</li><li>Use CDN for static assets</li></ul>",
            metadata={
                "source": "web_guide.html",
                "format_type": "html",
                "has_images": False,
                "has_tables": False,
                "structure_preserved": True
            }
        )
    ]
    
    # Markdown chunks for baseline comparison
    markdown_chunks = [
        Document(
            page_content="# API Documentation\n\nComplete guide to our REST API endpoints and authentication methods.",
            metadata={
                "source": "api_docs.md",
                "format_type": "markdown",
                "Header 1": "API Documentation",
                "structure_preserved": True
            }
        ),
        Document(
            page_content="## Authentication\n\n- API Key authentication\n- OAuth 2.0 support\n- Rate limiting: 1000 requests/hour",
            metadata={
                "source": "api_docs.md",
                "format_type": "markdown",
                "Header 2": "Authentication",
                "structure_preserved": True
            }
        )
    ]
    
    return {
        "pdf": pdf_chunks,
        "docx": docx_chunks,
        "image": image_chunks,
        "html": html_chunks,
        "markdown": markdown_chunks
    }


def demonstrate_multi_format_evaluation():
    """Demonstrate multi-format quality evaluation capabilities."""
    
    print("🚀 Multi-Format Quality Evaluator Demo - Story 1.4")
    print("=" * 60)
    
    # Initialize evaluators
    base_evaluator = ChunkQualityEvaluator()
    multi_format_evaluator = MultiFormatQualityEvaluator(base_evaluator)
    
    # Create sample chunks
    sample_chunks = create_sample_chunks()
    
    # Evaluate each format
    results = {}
    
    for format_type, chunks in sample_chunks.items():
        print(f"\n📊 Evaluating {format_type.upper()} Format:")
        print("-" * 40)
        
        # Perform evaluation
        result = multi_format_evaluator.evaluate_multi_format_chunks(chunks, format_type)
        results[format_type] = result
        
        # Display key metrics
        print(f"Total Chunks: {result.get('total_chunks', 0)}")
        print(f"Base Quality Score: {result.get('base_score', 0):.1f}/100")
        print(f"Format-Adjusted Score: {result.get('format_adjusted_score', 0):.1f}/100")
        
        # Format-specific metrics
        format_metrics = result.get('format_specific_metrics', {})
        print(f"Document Structure Score: {format_metrics.get('document_structure_score', 0):.2f}")
        print(f"Visual Content Score: {format_metrics.get('visual_content_score', 0):.2f}")
        print(f"Format Preservation Score: {format_metrics.get('format_preservation_score', 0):.2f}")
        
        # Performance metrics
        perf_metrics = result.get('performance_metrics', {})
        print(f"Evaluation Time: {perf_metrics.get('evaluation_time', 0):.3f}s")
        print(f"Avg Time per Chunk: {perf_metrics.get('avg_time_per_chunk', 0):.3f}s")
        
        # Comparative analysis
        comparative = result.get('comparative_analysis', {})
        baseline = comparative.get('markdown_baseline_comparison', {})
        if baseline:
            print(f"Relative Performance vs Markdown: {baseline.get('relative_performance', 0):.2f}")
            print(f"Performance Category: {baseline.get('performance_category', 'unknown')}")
    
    # Cross-format comparison
    print(f"\n🔄 Cross-Format Comparison:")
    print("-" * 40)
    
    format_scores = {}
    for format_type, result in results.items():
        format_scores[format_type] = result.get('format_adjusted_score', 0)
    
    # Sort by score
    sorted_formats = sorted(format_scores.items(), key=lambda x: x[1], reverse=True)
    
    print("Format Quality Ranking:")
    for i, (format_type, score) in enumerate(sorted_formats, 1):
        print(f"{i}. {format_type.upper()}: {score:.1f}/100")
    
    # Best performing format analysis
    best_format, best_score = sorted_formats[0]
    best_result = results[best_format]
    
    print(f"\n🏆 Best Performing Format: {best_format.upper()}")
    print("-" * 40)
    
    insights = best_result.get('format_insights', {})
    highlights = insights.get('quality_highlights', [])
    if highlights:
        print("Quality Highlights:")
        for highlight in highlights:
            print(f"  ✅ {highlight}")
    
    recommendations = insights.get('recommendations', [])
    if recommendations:
        print("Recommendations:")
        for rec in recommendations:
            print(f"  💡 {rec}")
    
    # Performance tracking summary
    print(f"\n⚡ Performance Summary:")
    print("-" * 40)
    
    total_time = sum(r.get('performance_metrics', {}).get('evaluation_time', 0) for r in results.values())
    total_chunks = sum(r.get('total_chunks', 0) for r in results.values())
    
    print(f"Total Evaluation Time: {total_time:.3f}s")
    print(f"Total Chunks Processed: {total_chunks}")
    print(f"Average Time per Chunk: {total_time/total_chunks:.3f}s")
    
    # Generate sample report
    print(f"\n📄 Sample Multi-Format Report:")
    print("-" * 40)
    
    # Generate report for best performing format
    report_path = "multi_format_quality_report.md"
    report = multi_format_evaluator.generate_multi_format_report(
        sample_chunks[best_format], 
        best_format, 
        report_path
    )
    
    print(f"Report saved to: {report_path}")
    print("\nReport Preview:")
    print(report[:500] + "..." if len(report) > 500 else report)
    
    print(f"\n✅ Demo Complete!")
    print("Multi-format quality evaluation successfully demonstrated.")
    print("All formats processed with enhanced metrics and comparative analysis.")


def demonstrate_visual_content_evaluation():
    """Demonstrate visual content evaluation capabilities."""
    
    print(f"\n🖼️  Visual Content Evaluation Demo:")
    print("-" * 40)
    
    base_evaluator = ChunkQualityEvaluator()
    multi_format_evaluator = MultiFormatQualityEvaluator(base_evaluator)
    
    # Create image chunks with different OCR qualities
    image_chunks = [
        Document(
            page_content="QUARTERLY SALES REPORT\n\nQ1: $1.2M\nQ2: $1.5M\nQ3: $1.8M",
            metadata={
                "source": "high_quality_chart.png",
                "format_type": "image",
                "ocr_confidence": 0.95,
                "image_type": "chart",
                "has_text": True,
                "structure_preserved": True
            }
        ),
        Document(
            page_content="blurry text extract... difficult to read...",
            metadata={
                "source": "low_quality_scan.png",
                "format_type": "image",
                "ocr_confidence": 0.65,
                "image_type": "document",
                "has_text": True,
                "structure_preserved": False
            }
        )
    ]
    
    # Evaluate visual content
    for i, chunk in enumerate(image_chunks, 1):
        print(f"\nImage {i}: {chunk.metadata['source']}")
        
        # Visual content evaluation
        visual_result = multi_format_evaluator.evaluate_visual_content(chunk)
        
        print(f"  OCR Confidence: {visual_result['ocr_confidence']:.2f}")
        print(f"  Text Extraction Quality: {visual_result['text_extraction_quality']:.2f}")
        print(f"  Visual Content Type: {visual_result['visual_content_type']}")
        print(f"  Visual Complexity: {visual_result['visual_complexity']:.2f}")
        
        # Format-specific scoring
        format_score = multi_format_evaluator.calculate_format_specific_score(chunk, "image")
        print(f"  Format-Specific Score: {format_score:.2f}")


def demonstrate_comparative_analysis():
    """Demonstrate comparative analysis against Markdown baseline."""
    
    print(f"\n📈 Comparative Analysis Demo:")
    print("-" * 40)
    
    base_evaluator = ChunkQualityEvaluator()
    multi_format_evaluator = MultiFormatQualityEvaluator(base_evaluator)
    
    # Test different content types
    test_cases = [
        ("High Quality PDF", 0.85, "structured_document"),
        ("Average DOCX", 0.72, "word_document"),
        ("Poor OCR Image", 0.45, "image_document"),
        ("Excellent HTML", 0.91, "web_content")
    ]
    
    print("Comparative Analysis Results:")
    
    for name, score, content_type in test_cases:
        comparison = multi_format_evaluator.benchmark_against_markdown(score, content_type)
        
        print(f"\n{name}:")
        print(f"  Score: {score:.2f}")
        print(f"  Relative Performance: {comparison['relative_performance']:.2f}")
        print(f"  Quality Differential: {comparison['quality_differential']:.2f}")
        print(f"  Category: {comparison['performance_category']}")
        
        if comparison['recommendations']:
            print(f"  Recommendations: {comparison['recommendations'][0]}")


if __name__ == "__main__":
    try:
        demonstrate_multi_format_evaluation()
        demonstrate_visual_content_evaluation()
        demonstrate_comparative_analysis()
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()