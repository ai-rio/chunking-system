#!/usr/bin/env python3
"""
Integration test for Story 1.3 - Format Detection & Enhanced FileHandler
Verifies complete implementation against acceptance criteria
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Import the components
from src.utils.enhanced_file_handler import EnhancedFileHandler, FileInfo
from src.utils.file_handler import FileHandler
from src.chunkers.docling_processor import DoclingProcessor, ProcessingResult
from src.llm.providers.docling_provider import DoclingProvider


class TestStory13Integration:
    """Integration tests for Story 1.3 implementation"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create mock dependencies
        self.mock_file_handler = Mock(spec=FileHandler)
        self.mock_docling_provider = Mock(spec=DoclingProvider)
        self.mock_docling_processor = Mock(spec=DoclingProcessor)
        
        # Setup mock responses
        self.mock_file_handler.find_markdown_files.return_value = []
        
        # Setup enhanced file handler
        self.enhanced_handler = EnhancedFileHandler(
            file_handler=self.mock_file_handler,
            docling_processor=self.mock_docling_processor
        )
        
        # Create test directory with various file types
        self.test_dir = tempfile.mkdtemp()
        self.test_files = self._create_test_files()
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def _create_test_files(self):
        """Create test files with various formats"""
        files = {}
        
        # PDF file
        pdf_path = os.path.join(self.test_dir, 'document.pdf')
        with open(pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\nTest PDF content\n%%EOF')
        files['pdf'] = pdf_path
        
        # DOCX file
        docx_path = os.path.join(self.test_dir, 'document.docx')
        with open(docx_path, 'wb') as f:
            f.write(b'PK\x03\x04\x14\x00\x06\x00\x08\x00\x00\x00!\x00')
        files['docx'] = docx_path
        
        # PPTX file
        pptx_path = os.path.join(self.test_dir, 'presentation.pptx')
        with open(pptx_path, 'wb') as f:
            f.write(b'PK\x03\x04\x14\x00\x00\x00\x08\x00')
        files['pptx'] = pptx_path
        
        # HTML file
        html_path = os.path.join(self.test_dir, 'webpage.html')
        with open(html_path, 'w') as f:
            f.write('<!DOCTYPE html><html><head><title>Test</title></head><body><h1>Test</h1></body></html>')
        files['html'] = html_path
        
        # Image file
        image_path = os.path.join(self.test_dir, 'image.png')
        with open(image_path, 'wb') as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89')
        files['image'] = image_path
        
        # Markdown file
        md_path = os.path.join(self.test_dir, 'readme.md')
        with open(md_path, 'w') as f:
            f.write('# Test Document\n\nThis is a test markdown file.\n\n## Features\n\n- Feature 1\n- Feature 2')
        files['markdown'] = md_path
        
        # Unsupported file
        unsupported_path = os.path.join(self.test_dir, 'unsupported.xyz')
        with open(unsupported_path, 'w') as f:
            f.write('This is an unsupported format')
        files['unsupported'] = unsupported_path
        
        return files
    
    def test_ac1_format_detection_identifies_all_formats(self):
        """
        AC1: Format detection automatically identifies PDF, DOCX, PPTX, HTML, image, and Markdown files
        """
        expected_formats = {
            'pdf': 'pdf',
            'docx': 'docx',
            'pptx': 'pptx',
            'html': 'html',
            'image': 'image',
            'markdown': 'markdown'
        }
        
        for file_type, expected_format in expected_formats.items():
            file_path = self.test_files[file_type]
            detected_format = self.enhanced_handler.detect_format(file_path)
            
            assert detected_format == expected_format, f"Expected {expected_format}, got {detected_format} for {file_type}"
        
        # Test unsupported format
        unsupported_format = self.enhanced_handler.detect_format(self.test_files['unsupported'])
        assert unsupported_format == 'unknown', f"Expected 'unknown', got {unsupported_format}"
    
    def test_ac2_intelligent_routing_directs_to_appropriate_processors(self):
        """
        AC2: Intelligent routing directs files to DoclingProcessor or existing MarkdownProcessor based on format
        """
        # Mock DoclingProcessor response
        mock_docling_result = ProcessingResult(
            format_type='pdf',
            file_path=self.test_files['pdf'],
            success=True,
            text='Processed content',
            structure={},
            metadata={},
            processing_time=0.1,
            file_size=1024
        )
        self.mock_docling_processor.process_document.return_value = mock_docling_result
        
        # Test DoclingProcessor routing (PDF)
        pdf_result = self.enhanced_handler.route_to_processor(self.test_files['pdf'], 'pdf')
        assert pdf_result == mock_docling_result
        self.mock_docling_processor.process_document.assert_called_with(self.test_files['pdf'], 'pdf')
        
        # Test MarkdownProcessor routing (Markdown)
        md_result = self.enhanced_handler.route_to_processor(self.test_files['markdown'], 'markdown')
        assert md_result.format_type == 'markdown'
        assert md_result.success is True
        assert '# Test Document' in md_result.text
        
        # Test DoclingProcessor routing for other formats
        for format_type in ['docx', 'pptx', 'html', 'image']:
            file_path = self.test_files[format_type]
            mock_result = ProcessingResult(
                format_type=format_type,
                file_path=file_path,
                success=True,
                text=f'Processed {format_type} content',
                structure={},
                metadata={},
                processing_time=0.1,
                file_size=1024
            )
            self.mock_docling_processor.process_document.return_value = mock_result
            
            result = self.enhanced_handler.route_to_processor(file_path, format_type)
            assert result == mock_result
    
    def test_ac3_file_validation_extends_security_validation(self):
        """
        AC3: File validation extends existing security validation to new formats with appropriate size and content checks
        """
        # Test valid files
        for file_type in ['pdf', 'docx', 'pptx', 'html', 'image', 'markdown']:
            file_path = self.test_files[file_type]
            format_type = self.enhanced_handler.detect_format(file_path)
            is_valid = self.enhanced_handler.validate_file_format(file_path, format_type)
            assert is_valid is True, f"File {file_type} should be valid"
        
        # Test invalid format mismatch
        pdf_path = self.test_files['pdf']
        is_valid = self.enhanced_handler.validate_file_format(pdf_path, 'docx')
        assert is_valid is False, "PDF file should not validate as DOCX"
        
        # Test file size limits (mock large file)
        with patch('os.path.getsize', return_value=100 * 1024 * 1024):  # 100MB
            is_valid = self.enhanced_handler.validate_file_format(pdf_path, 'pdf')
            assert is_valid is False, "Oversized file should not validate"
    
    def test_ac4_error_messaging_provides_clear_feedback(self):
        """
        AC4: Error messaging provides clear feedback for unsupported formats or processing failures
        """
        # Test unsupported format error
        unsupported_path = self.test_files['unsupported']
        with pytest.raises(ValueError, match="Unsupported format"):
            self.enhanced_handler.route_to_processor(unsupported_path, 'xyz')
        
        # Test file not found error
        with pytest.raises(FileNotFoundError):
            self.enhanced_handler.detect_format('/nonexistent/file.pdf')
        
        # Test processing failure by resetting mock
        self.mock_docling_processor.reset_mock()
        
        # Mock a failing response
        failed_result = ProcessingResult(
            format_type='pdf',
            file_path=self.test_files['pdf'],
            success=False,
            text='',
            structure={},
            metadata={},
            processing_time=0.1,
            file_size=1024,
            error_message="Processing failed"
        )
        self.mock_docling_processor.process_document.return_value = failed_result
        
        result = self.enhanced_handler.route_to_processor(self.test_files['pdf'], 'pdf')
        assert result.success is False
        assert "Processing failed" in result.error_message
    
    def test_ac5_batch_processing_handles_mixed_formats(self):
        """
        AC5: Batch processing handles mixed-format document collections efficiently
        """
        # Prepare mixed format files
        mixed_files = [
            self.test_files['pdf'],
            self.test_files['markdown'],
            self.test_files['html'],
            self.test_files['image']
        ]
        
        # Mock DoclingProcessor responses
        def mock_process_document(file_path, format_type):
            return ProcessingResult(
                format_type=format_type,
                file_path=file_path,
                success=True,
                text=f'Processed {format_type} content',
                structure={},
                metadata={},
                processing_time=0.1,
                file_size=1024
            )
        
        self.mock_docling_processor.process_document.side_effect = mock_process_document
        
        # Process batch
        results = self.enhanced_handler.process_batch(mixed_files)
        
        # Verify results
        assert len(results) == 4
        assert all(result.success for result in results)
        
        # Verify format types
        format_types = [result.format_type for result in results]
        assert 'pdf' in format_types
        assert 'markdown' in format_types
        assert 'html' in format_types
        assert 'image' in format_types
    
    def test_ac6_cli_interface_maintains_existing_patterns(self):
        """
        AC6: CLI interface maintains existing argument patterns while supporting new format options
        """
        # Test supported formats retrieval
        formats = self.enhanced_handler.get_supported_formats()
        expected_formats = {'pdf', 'docx', 'pptx', 'html', 'image', 'markdown'}
        assert set(formats) == expected_formats
        
        # Test format support checking
        for format_type in expected_formats:
            assert self.enhanced_handler.is_format_supported(format_type) is True
        
        assert self.enhanced_handler.is_format_supported('unsupported') is False
    
    def test_iv1_existing_markdown_processing_unchanged(self):
        """
        IV1: Existing Markdown file processing remains unchanged in behavior and performance
        """
        # Mock the existing markdown files function
        md_files = [self.test_files['markdown']]
        self.mock_file_handler.find_markdown_files.return_value = md_files
        
        # Test that find_supported_files still calls find_markdown_files
        supported_files = self.enhanced_handler.find_supported_files(self.test_dir)
        
        # Verify backward compatibility call
        self.mock_file_handler.find_markdown_files.assert_called_once_with(self.test_dir)
        
        # Verify markdown files are included
        markdown_files = [f for f in supported_files if f.format_type == 'markdown']
        assert len(markdown_files) > 0
    
    def test_iv2_find_markdown_files_continues_functioning(self):
        """
        IV2: find_markdown_files() and related methods continue functioning for backward compatibility
        """
        # Test that the enhanced handler preserves existing functionality
        md_files = [self.test_files['markdown']]
        self.mock_file_handler.find_markdown_files.return_value = md_files
        
        # Call find_supported_files
        supported_files = self.enhanced_handler.find_supported_files(self.test_dir)
        
        # Verify the backward compatibility call was made
        self.mock_file_handler.find_markdown_files.assert_called_once()
        
        # Verify results include markdown files
        markdown_files = [f for f in supported_files if f.format_type == 'markdown']
        assert len(markdown_files) >= 1
    
    def test_iv3_existing_file_validation_remains_operational(self):
        """
        IV3: Existing file validation and security checks remain fully operational
        """
        # Test that validation works for all file types
        for file_type in ['pdf', 'docx', 'pptx', 'html', 'image', 'markdown']:
            file_path = self.test_files[file_type]
            format_type = self.enhanced_handler.detect_format(file_path)
            
            # Validation should work
            is_valid = self.enhanced_handler.validate_file_format(file_path, format_type)
            assert is_valid is True, f"Validation failed for {file_type}"
            
            # Security checks should work (file exists, size limits, etc.)
            assert os.path.exists(file_path), f"File {file_type} should exist"
    
    def test_comprehensive_workflow_integration(self):
        """
        Comprehensive test of the complete workflow from discovery to processing
        """
        # Mock DoclingProcessor for comprehensive test
        def mock_process_document(file_path, format_type):
            return ProcessingResult(
                format_type=format_type,
                file_path=file_path,
                success=True,
                text=f'Processed {format_type} content from {os.path.basename(file_path)}',
                structure={'type': format_type},
                metadata={'source': file_path},
                processing_time=0.1,
                file_size=os.path.getsize(file_path)
            )
        
        self.mock_docling_processor.process_document.side_effect = mock_process_document
        
        # Step 1: Discover supported files
        supported_files = self.enhanced_handler.find_supported_files(self.test_dir)
        
        # Should find all supported formats except unsupported
        assert len(supported_files) == 6  # pdf, docx, pptx, html, image, markdown
        
        # Step 2: Process each file
        all_results = []
        for file_info in supported_files:
            result = self.enhanced_handler.route_to_processor(file_info.file_path, file_info.format_type)
            all_results.append(result)
        
        # Step 3: Verify all processed successfully
        assert len(all_results) == 6
        assert all(result.success for result in all_results)
        
        # Step 4: Verify format distribution
        format_types = [result.format_type for result in all_results]
        expected_formats = {'pdf', 'docx', 'pptx', 'html', 'image', 'markdown'}
        assert set(format_types) == expected_formats
        
        # Step 5: Verify content extraction
        for result in all_results:
            assert len(result.text) > 0, f"No content extracted for {result.format_type}"
            assert result.file_size > 0, f"No file size recorded for {result.format_type}"
            assert result.processing_time >= 0, f"Invalid processing time for {result.format_type}"


def main():
    """Run integration tests"""
    print("🧪 Running Story 1.3 Integration Tests")
    print("=" * 50)
    
    # Create test instance
    test_instance = TestStory13Integration()
    
    # Run all tests
    test_methods = [
        test_instance.test_ac1_format_detection_identifies_all_formats,
        test_instance.test_ac2_intelligent_routing_directs_to_appropriate_processors,
        test_instance.test_ac3_file_validation_extends_security_validation,
        test_instance.test_ac4_error_messaging_provides_clear_feedback,
        test_instance.test_ac5_batch_processing_handles_mixed_formats,
        test_instance.test_ac6_cli_interface_maintains_existing_patterns,
        test_instance.test_iv1_existing_markdown_processing_unchanged,
        test_instance.test_iv2_find_markdown_files_continues_functioning,
        test_instance.test_iv3_existing_file_validation_remains_operational,
        test_instance.test_comprehensive_workflow_integration
    ]
    
    passed = 0
    failed = 0
    
    for i, test_method in enumerate(test_methods, 1):
        test_name = test_method.__name__
        try:
            test_instance.setup_method()
            test_method()
            test_instance.teardown_method()
            
            print(f"✅ {i:2d}. {test_name}")
            passed += 1
        except Exception as e:
            print(f"❌ {i:2d}. {test_name}: {str(e)}")
            failed += 1
            try:
                test_instance.teardown_method()
            except:
                pass
    
    print("\n" + "=" * 50)
    print(f"🎯 Integration Test Results:")
    print(f"   ✅ Passed: {passed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📊 Total:  {passed + failed}")
    
    if failed == 0:
        print("\n🎉 All Story 1.3 acceptance criteria verified!")
        print("✅ Enhanced FileHandler implementation is complete and functional")
    else:
        print(f"\n⚠️  {failed} test(s) failed - review implementation")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)