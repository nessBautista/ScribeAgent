import pytest
from unittest.mock import Mock, patch

from scribeagent.application.services.notion_services import NotionPageService
from scribeagent.domain.notion.entities import Page, Block, ParagraphBlock
from scribeagent.domain.notion.repositories import PageRepository
from scribeagent.utils.NotionAPIUrlParser import NotionAPIUrlParser
from scribeagent.domain.notion.enums import NotionObjectType, BlockType
from datetime import datetime


class TestNotionPageService:
    """Tests for the NotionPageService."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.page_repository = Mock(spec=PageRepository)
        self.url_parser = Mock(spec=NotionAPIUrlParser)
        self.service = NotionPageService(self.page_repository, self.url_parser)
        
        # Create a sample page and blocks for testing
        self.sample_page = self._create_sample_page()
        self.sample_blocks = self._create_sample_blocks()
        
        # Configure mocks
        self.page_repository.get_page.return_value = self.sample_page
        self.page_repository.get_page_content.return_value = self.sample_blocks
        self.url_parser.extract_id_from_url.return_value = "test_page_id"
    
    def _create_sample_page(self):
        """Create a sample page for testing."""
        return Mock(spec=Page, id="test_page_id", object_type=NotionObjectType.PAGE)
    
    def _create_sample_blocks(self):
        """Create sample blocks for testing."""
        return [
            Mock(spec=ParagraphBlock, id="block1", block_type=BlockType.PARAGRAPH),
            Mock(spec=ParagraphBlock, id="block2", block_type=BlockType.PARAGRAPH)
        ]
    
    def test_get_page_by_url(self):
        """Test getting a page by URL."""
        # Call the method
        page = self.service.get_page_by_url("https://www.notion.so/test-page-123")
        
        # Verify the URL was parsed
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page.assert_called_once_with("test_page_id")
        
        # Verify the result
        assert page == self.sample_page
    
    def test_get_page_content_by_url(self):
        """Test getting page content by URL."""
        # Call the method
        blocks = self.service.get_page_content_by_url("https://www.notion.so/test-page-123")
        
        # Verify the URL was parsed
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page_content.assert_called_once_with("test_page_id")
        
        # Verify the result
        assert blocks == self.sample_blocks
    
    def test_get_page_with_content_using_url(self):
        """Test getting a page with content using a URL."""
        # Call the method
        page, blocks = self.service.get_page_with_content("https://www.notion.so/test-page-123")
        
        # Verify the URL was parsed
        self.url_parser.extract_id_from_url.assert_called_once_with("https://www.notion.so/test-page-123")
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page.assert_called_once_with("test_page_id")
        self.page_repository.get_page_content.assert_called_once_with("test_page_id")
        
        # Verify the results
        assert page == self.sample_page
        assert blocks == self.sample_blocks
    
    def test_get_page_with_content_using_id(self):
        """Test getting a page with content using an ID directly."""
        # Call the method
        page, blocks = self.service.get_page_with_content("direct_page_id")
        
        # Verify the URL parser was not called
        self.url_parser.extract_id_from_url.assert_not_called()
        
        # Verify the repository was called with the correct ID
        self.page_repository.get_page.assert_called_once_with("direct_page_id")
        self.page_repository.get_page_content.assert_called_once_with("direct_page_id")
        
        # Verify the results
        assert page == self.sample_page
        assert blocks == self.sample_blocks
    
    def test_integration_with_real_dependencies(self):
        """Test with real dependencies (but mocked repositories)."""
        # Create a real URL parser and mock repository
        real_url_parser = NotionAPIUrlParser()
        mock_repository = Mock(spec=PageRepository)
        mock_repository.get_page.return_value = self.sample_page
        mock_repository.get_page_content.return_value = self.sample_blocks
        
        # Create service with real parser
        service = NotionPageService(mock_repository, real_url_parser)
        
        # Test with a real Notion URL
        test_url = "https://www.notion.so/Test-Page-abc123def456"
        page, blocks = service.get_page_with_content(test_url)
        
        # Verify the repository was called with the correct extracted ID
        mock_repository.get_page.assert_called_once_with("abc123def456")
        mock_repository.get_page_content.assert_called_once_with("abc123def456")
        
        # Verify the results
        assert page == self.sample_page
        assert blocks == self.sample_blocks 